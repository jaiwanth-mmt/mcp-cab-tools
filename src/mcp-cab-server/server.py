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

async def periodic_cleanup():
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        expired = cleanup_expired_holds()
        if expired > 0:
            logger.info(f"🧹 Cleaned up {expired} expired holds")

async def get_location_with_disambiguation(
    ctx: Context, 
    location_query: str, 
    location_type: str
) -> tuple:
    """
    Geocode a location and handle disambiguation with recursive refinement.
    """
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


if __name__ == "__main__":
    import threading
    
    
    def cleanup_thread():
        import time
        while True:
            time.sleep(300)
            cleanup_expired_holds()
    
    threading.Thread(target=cleanup_thread, daemon=True).start()
    mcp.run()