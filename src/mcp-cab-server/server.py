from dotenv import load_dotenv
load_dotenv()
from fastmcp import FastMCP , Context
from models.models import  SearchRequest, SearchResponse , HoldCabRequest , HoldCabResponse , PassengerDetailsRequest , PassengerDetailsResponse
import logging
from services.helper import get_available_cabs
from services.geocoding import geocode_location , resolve_location_by_place_id
from services.helper import hold_cab , add_passenger_details_to_hold
from datetime import datetime , date
from services.mock_db import cleanup_expired_holds
import asyncio

# Load environment variables from .env file



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("cab-server")



async def get_location_with_disambiguation(
    ctx: Context, 
    location_query: str, 
    location_type: str
) -> tuple:
    logger.info(f"📍 Geocoding {location_type} location: {location_query}")
    results = await geocode_location(location_query)
    
    if not results:
        return None, f"No locations found for {location_type}: {location_query}"
    
   
    if len(results) == 1:
        loc = results[0]
        location = await resolve_location_by_place_id(loc.place_id)
        if not location:
            return None, f"Failed to get details for {location_type}: '{loc.name}'. Please try again."
        logger.info(f"✅ Single {location_type} location found: {location.name}")
        return location, None
    
    logger.info(f"Multiple {location_type} locations detected ({len(results)}), requesting user selection")
    
    options_dict = {
        loc.place_id: {
            "title": f"{loc.name} - {loc.formatted_address}"
        }
        for loc in results
    }
    
    options_dict["__CUSTOM__"] = {
        "title": f"🔄 None of these - let me specify a different location"
    }
    
    response = await ctx.elicit(
        message=f"🚕 Found {len(results)} locations for '{location_query}'. Please select the {location_type} location:",
        response_type=options_dict
    )
    
    place_id = response.data
    
    if not place_id:
        return None, f"No {location_type} location selected"
    
    if place_id == "__CUSTOM__":
        logger.info(f"User requested custom {location_type} location")
        custom_response = await ctx.elicit(
            message=f"📍 Please enter a more specific {location_type} location:\n💡 Tip: Include area, landmark, or sector (e.g., 'Mumbai Airport Terminal 2', 'Noida Sector 62', 'Whitefield ITPL')",
            response_type=str
        )
        custom_location_query = custom_response.data
        
        if not custom_location_query:
            return None, f"No custom {location_type} location provided"
        
        logger.info(f"🔍 Re-geocoding with user-specified location: {custom_location_query}")
        return await get_location_with_disambiguation(
            ctx, 
            custom_location_query,
            location_type
        )
    
    location = await resolve_location_by_place_id(place_id)
    if not location:
        return None, f"Failed to resolve {location_type} location. Please try a different search."
    logger.info(f"✅ User selected {location_type}: {location.name}")
    return location, None



@mcp.tool(name="Search_cabs" , description="Cabs to search")
async def search_cabs(ctx:Context , input: SearchRequest)->SearchResponse:
    logger.info(f"🔍 Cab search request - Pickup: {input.pickup}, Drop: {input.drop}")
    try:
        pickup_location , pickup_error = await get_location_with_disambiguation(ctx , input.pickup , "pickup")
        if pickup_error:
            await ctx.info(f"❌ {pickup_error}")
            return SearchResponse(cabs = [])
    except ValueError as e:
        await ctx.info(f"❌ System error: {str(e)}")
        return SearchResponse(cabs=[])
    try:
        drop_location , drop_error = await get_location_with_disambiguation(ctx , input.drop , "drop")
        if drop_error:
            await ctx.info(f"❌ {drop_error}")
            return SearchResponse(cabs = [])
    except ValueError as e:
        await ctx.info(f"❌ System error: {str(e)}")
        return SearchResponse(cabs=[])
    logger.info(f"✅ Locations resolved - Pickup: {pickup_location.name}, Drop: {drop_location.name}")
    available_cabs = get_available_cabs(pickup_location.name.lower(), drop_location.name.lower())
    if not available_cabs.cabs:
        await ctx.info(
            f"⚠️ No cabs available for route:\n"
            f"📍 From: {pickup_location.name}\n"
            f"📍 To: {drop_location.name}\n"
            f"Please try a different route or time."
        )
    return available_cabs


@mcp.tool(name="hold_cab_booking" ,description="Create temporary cab reservation with 15-minute hold")
async def hold_cab_booking(ctx:Context , input: HoldCabRequest )->HoldCabResponse:
    logger.info(f"🔒 Hold cab request - Cab ID: {input.cab_id}, Date: {input.departure_date}")
    try:
        # Create the hold
        hold_response = hold_cab(
            cab_id=input.cab_id,
            pickup=input.pickup,
            drop=input.drop,
            departure_date=input.departure_date.isoformat() if isinstance(input.departure_date, date) else input.departure_date
        )
        
        logger.info(f"✅ Hold created successfully: {hold_response.hold_id}")
        await ctx.info(
            f"🎉 Cab Reserved!\n\n"
            f"Hold ID: {hold_response.hold_id}\n"
            f"Cab Type: {hold_response.cab_details['cab_type']}\n"
            f"Price: ₹{hold_response.price}\n"
            f"Valid until: {datetime.fromisoformat(hold_response.expires_at).strftime('%I:%M %p')}\n"
            f"⏰ Please complete passenger details and payment within 15 minutes."
        )
        return hold_response
    except ValueError as e:
        logger.error(f"❌ Hold creation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during hold creation: {str(e)}")
        raise ValueError(f"Failed to create hold: {str(e)}")

@mcp.tool(
    name="add_passenger_details", 
    description="Add passenger information to cab booking hold"
)
async def add_passenger_details(
    ctx: Context, 
    input: PassengerDetailsRequest
) -> PassengerDetailsResponse:
    
    logger.info(f"👤 Add passenger request - Hold: {input.hold_id}, Name: {input.passenger_name}")
    
    try:
        # Add passenger details
        response = add_passenger_details_to_hold(
            hold_id=input.hold_id,
            passenger_name=input.passenger_name,
            passenger_phone=input.passenger_phone,
            passenger_email=input.passenger_email,
            special_requests=input.special_requests
        )
        
        logger.info(f"✅ Passenger details added successfully to hold: {input.hold_id}")
        
        # Show confirmation to user
        email_text = f"\n📧 Email: {response.passenger_email}" if response.passenger_email else ""
        special_req_text = f"\n📝 Special Requests: {response.special_requests}" if response.special_requests else ""
        
        await ctx.info(
            f"✅ Passenger Details Saved!\n\n"
            f"👤 Name: {response.passenger_name}\n"
            f"📱 Phone: {response.passenger_phone}"
            f"{email_text}"
            f"{special_req_text}\n\n"
            f"🎫 Booking Summary:\n"
            f"   • Cab: {response.booking_summary['cab_type']}\n"
            f"   • Route: {response.booking_summary['pickup']} → {response.booking_summary['drop']}\n"
            f"   • Date: {response.booking_summary['departure_date']}\n"
            f"   • Price: ₹{response.booking_summary['price']}\n\n"
            f"⏰ Hold expires at: {response.expires_at}\n"
            f"✅ Ready for payment!"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"❌ Failed to add passenger details: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise ValueError(f"Failed to add passenger details: {str(e)}")


@mcp.tool(
    name="create_payment_order",
    description="Generate mock payment link for cab booking hold"
)
async def create_payment_order(
    ctx: Context,
    hold_id: str
) -> dict:
    logger.info(f"💳 Payment order creation request for hold: {hold_id}")
    
    try:
        from services.payment import create_payment_order_internal
        
        payment_order = create_payment_order_internal(hold_id)
        
        logger.info(f"🔗 Prompting user to open payment URL")
        
        result = await ctx.elicit(
            message=(
                f"💳 Payment link ready for your cab booking!\n\n"
                f"**Amount:** ₹{payment_order.amount:.2f}\n"
                f"**Session ID:** {payment_order.session_id}\n"
                f"**Valid until:** {payment_order.expires_at}\n\n"
                f"🔗 **Payment URL:**\n{payment_order.payment_url}\n\n"
                f"Please open this URL in your browser to complete payment.\n"
                f"After payment, use `verify_mock_payment` to check status.\n\n"
                f"Did you open the payment URL?"
            ),
            response_type=None
        )
        
        if result.action == "accept":
            await ctx.info(
                f"✅ Payment URL provided!\n\n"
                f"📋 Payment Details:\n"
                f"   • Session ID: {payment_order.session_id}\n"
                f"   • Amount: ₹{payment_order.amount:.2f}\n"
                f"   • Hold ID: {hold_id}\n"
                f"   • Expires: {payment_order.expires_at}\n\n"
                f"💡 Next Steps:\n"
                f"   1. Complete payment in your browser\n"
                f"   2. Use `verify_mock_payment('{payment_order.session_id}')` to check status\n"
                f"   3. Use `confirm_booking('{hold_id}')` after payment completes"
            )
        elif result.action == "decline":
            await ctx.info(
                f"❌ Payment link declined.\n\n"
                f"Session ID: {payment_order.session_id} (created but not opened)\n"
                f"You can still open the URL later if needed."
            )
        else:  # cancel
            await ctx.info(
                f"⚠️ Payment operation cancelled.\n\n"
                f"Session ID: {payment_order.session_id} (created but cancelled)"
            )
        
        return {
            "session_id": payment_order.session_id,
            "payment_url": payment_order.payment_url,
            "amount": payment_order.amount,
            "hold_id": payment_order.hold_id,
            "expires_at": payment_order.expires_at,
            "created_at": payment_order.created_at,
            "status": "initiated"
        }
        
    except ValueError as e:
        logger.error(f"❌ Payment order creation failed: {str(e)}")
        await ctx.info(f"❌ Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        await ctx.info(f"❌ Unexpected error: {str(e)}")
        raise ValueError(f"Failed to create payment order: {str(e)}")


@mcp.tool(
    name="verify_mock_payment",
    description="Check payment completion status for a session"
)
async def verify_mock_payment(
    ctx: Context,
    session_id: str
) -> dict:
    logger.info(f"🔍 Payment verification request for session: {session_id}")
    
    try:
        from services.payment import get_payment_status_internal
        
        payment_status = get_payment_status_internal(session_id)
        
        status_str = payment_status.status.value
        
        if payment_status.status.value == "completed":
            await ctx.info(
                f"✅ Payment Completed!\n\n"
                f"📋 Payment Details:\n"
                f"   • Session ID: {session_id}\n"
                f"   • Status: {status_str.upper()}\n"
                f"   • Amount: ₹{payment_status.amount:.2f}\n"
                f"   • Hold ID: {payment_status.hold_id}\n"
                f"   • Completed: {payment_status.completed_at}\n"
                f"   • Card: •••• {payment_status.card_last4 or 'N/A'}\n\n"
                f"✅ Payment successfully processed!\n"
                f"💡 Next: Use `confirm_booking('{payment_status.hold_id}')` to finalize booking."
            )
        elif payment_status.status.value == "pending":
            await ctx.info(
                f"⏳ Payment Pending\n\n"
                f"📋 Payment Details:\n"
                f"   • Session ID: {session_id}\n"
                f"   • Status: {status_str.upper()}\n"
                f"   • Amount: ₹{payment_status.amount:.2f}\n"
                f"   • Hold ID: {payment_status.hold_id}\n"
                f"   • Created: {payment_status.created_at}\n\n"
                f"⏳ Payment not completed yet.\n"
                f"The user may still be entering payment details in the browser."
            )
        else:  # failed
            await ctx.info(
                f"❌ Payment Failed\n\n"
                f"📋 Payment Details:\n"
                f"   • Session ID: {session_id}\n"
                f"   • Status: {status_str.upper()}\n"
                f"   • Amount: ₹{payment_status.amount:.2f}\n"
                f"   • Hold ID: {payment_status.hold_id}\n\n"
                f"❌ Payment could not be processed.\n"
                f"You may need to create a new payment order."
            )
        
        return {
            "session_id": payment_status.session_id,
            "status": status_str,
            "amount": payment_status.amount,
            "hold_id": payment_status.hold_id,
            "created_at": payment_status.created_at,
            "completed_at": payment_status.completed_at,
            "card_last4": payment_status.card_last4
        }
        
    except ValueError as e:
        logger.error(f"❌ Payment verification failed: {str(e)}")
        await ctx.info(f"❌ Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        await ctx.info(f"❌ Unexpected error: {str(e)}")
        raise ValueError(f"Failed to verify payment: {str(e)}")


@mcp.tool(
    name="confirm_booking",
    description="Finalize booking after payment and assign driver"
)
async def confirm_booking(
    ctx: Context,
    hold_id: str
) -> dict:
    logger.info(f"🎉 Booking confirmation request for hold: {hold_id}")
    
    try:
        from services.payment import confirm_booking_internal
        
        confirmation = confirm_booking_internal(hold_id)
        
        driver = confirmation.driver
        summary = confirmation.booking_summary
        
        await ctx.info(
            f"🎉 Booking Confirmed!\n\n"
            f"📋 Booking Details:\n"
            f"   • Booking ID: {confirmation.booking_id}\n"
            f"   • Hold ID: {hold_id}\n"
            f"   • Status: {confirmation.status.value.upper()}\n"
            f"   • Confirmed: {confirmation.confirmed_at}\n\n"
            f"🚗 Driver Assigned:\n"
            f"   • Name: {driver.name}\n"
            f"   • Phone: {driver.phone}\n"
            f"   • Vehicle: {driver.vehicle_model}\n"
            f"   • Number: {driver.vehicle_number}\n"
            f"   • Rating: {driver.rating} ⭐\n\n"
            f"🚕 Trip Details:\n"
            f"   • Cab Type: {summary['cab_type']}\n"
            f"   • Route: {summary['pickup']} → {summary['drop']}\n"
            f"   • Date: {summary['departure_date']}\n"
            f"   • Price: ₹{summary['price']}\n\n"
            f"👤 Passenger:\n"
            f"   • Name: {summary['passenger']['name']}\n"
            f"   • Phone: {summary['passenger']['phone']}\n\n"
            f"✅ Your cab booking is confirmed!\n"
            f"The driver will contact you before the trip."
        )
        
        return {
            "booking_id": confirmation.booking_id,
            "hold_id": confirmation.hold_id,
            "status": confirmation.status.value,
            "driver": {
                "name": driver.name,
                "phone": driver.phone,
                "vehicle_number": driver.vehicle_number,
                "vehicle_model": driver.vehicle_model,
                "rating": driver.rating
            },
            "booking_summary": summary,
            "confirmed_at": confirmation.confirmed_at
        }
        
    except ValueError as e:
        logger.error(f"❌ Booking confirmation failed: {str(e)}")
        await ctx.info(f"❌ Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        await ctx.info(f"❌ Unexpected error: {str(e)}")
        raise ValueError(f"Failed to confirm booking: {str(e)}")


if __name__ == "__main__":
    import threading
    
    def cleanup_thread():
        import time
        while True:
            time.sleep(300)
            cleanup_expired_holds()
    
    threading.Thread(target=cleanup_thread, daemon=True).start()
    mcp.run()