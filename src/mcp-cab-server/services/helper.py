from .mock_db import MOCK_CAB_DB , create_booking_hold ,  get_cab_by_id ,add_passenger_to_hold , get_passenger_details , is_hold_expired
from models.models import  SearchResponse , IndividualCabResponse , HoldCabResponse , BookingStatus  ,  PassengerDetailsResponse
from typing import List , Union
from services.logging_config import get_logger
from datetime import datetime , timedelta , date
logger = get_logger(__name__, service="helper")


def ensure_isoformat(value: Union[datetime, date, str]) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    return str(value)

DEFAULT_CABS = [
    {"cab_id": "DEF_CAB_MINI", "cab_type": "mini", "price": 300},
    {"cab_id": "DEF_CAB_SEDAN", "cab_type": "sedan", "price": 500},
    {"cab_id": "DEF_CAB_SUV", "cab_type": "suv", "price": 700},
    {"cab_id": "DEF_CAB_PRIME_SEDAN", "cab_type": "prime sedan", "price": 900},
]

def get_available_cabs(pickup: str, drop: str) -> SearchResponse:
    pickup_lower = pickup.lower()
    drop_lower = drop.lower()
    
    logger.info(
        "Searching for available cabs",
        extra={"pickup": pickup_lower, "drop": drop_lower}
    )
    
    exact_match = MOCK_CAB_DB.get((pickup_lower, drop_lower), None)
    if exact_match:
        logger.info(
            "Exact route match found in database",
            extra={
                "route": f"{pickup_lower} → {drop_lower}",
                "cab_count": len(exact_match)
            }
        )
        return SearchResponse(cabs=[
            IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
            for cab in exact_match
        ])
    
    logger.debug("No exact match, attempting fuzzy matching")
    
    for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
        pickup_keywords = [w for w in pickup_key.split() if len(w) > 3]
        drop_keywords = [w for w in drop_key.split() if len(w) > 3]
        
        pickup_match = any(keyword in pickup_lower for keyword in pickup_keywords)
        drop_match = any(keyword in drop_lower for keyword in drop_keywords)
        
        if pickup_match and drop_match:
            logger.info(
                "Fuzzy match found",
                extra={
                    "requested": f"{pickup_lower} → {drop_lower}",
                    "matched": f"{pickup_key} → {drop_key}",
                    "cab_count": len(cabs)
                }
            )
            return SearchResponse(cabs=[
                IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                for cab in cabs
            ])
    
    logger.debug("Checking for intra-city routes")
    
    cities = ["mumbai", "pune", "delhi", "bangalore", "hyderabad"]
    for city in cities:
        if city in pickup_lower and city in drop_lower:
            logger.info(
                "Intra-city route detected",
                extra={"city": city, "route": f"{pickup_lower} → {drop_lower}"}
            )
            for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
                if city in pickup_key and city in drop_key:
                    logger.debug(
                        "Found intra-city cab options",
                        extra={"matched_route": f"{pickup_key} → {drop_key}"}
                    )
                    return SearchResponse(cabs=[
                        IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                        for cab in cabs
                    ])
    
    logger.warning(
        "No specific route found, returning default cabs",
        extra={"pickup": pickup_lower, "drop": drop_lower}
    )

    return SearchResponse(cabs=[
        IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
        for cab in DEFAULT_CABS
    ])

def hold_cab(cab_id: str , pickup: str , drop: str , departure_date)->HoldCabResponse:
    logger.info(
        "Creating cab hold",
        extra={"cab_id": cab_id, "pickup": pickup, "drop": drop, "date": str(departure_date)}
    )
    
    cab_details = get_cab_by_id(cab_id)
    if not cab_details:
        logger.error(
            "Cab not found in database",
            extra={"cab_id": cab_id}
        )
        raise ValueError(f"Invalid cab_id: {cab_id}. Cab not found in search results.")
    
    hold_data = create_booking_hold(cab_id, pickup, drop, departure_date)
    
    if not hold_data:
        logger.error(
            "Failed to create booking hold",
            extra={"cab_id": cab_id, "pickup": pickup, "drop": drop}
        )
        raise ValueError("Failed to create booking hold")
    
    logger.info(
        "Hold created successfully",
        extra={
            "hold_id": hold_data['hold_id'],
            "cab_type": cab_details['cab_type'],
            "price": hold_data['price'],
            "expires_at": str(hold_data['expires_at'])
        }
    )
    
    return HoldCabResponse(
        hold_id=hold_data['hold_id'],
        cab_id=hold_data['cab_id'],
        status=BookingStatus.HELD,
        expires_at=ensure_isoformat(hold_data['expires_at']),
        cab_details=hold_data['cab_details'],
        price=hold_data['price'],
        pickup_location=hold_data['pickup_location'],
        drop_location=hold_data['drop_location'],
        departure_date=ensure_isoformat(hold_data['departure_date']),
        created_at=ensure_isoformat(hold_data['created_at'])
    )

def add_passenger_details_to_hold(hold_id: str , passenger_name: str , passenger_phone: str , passenger_email: str = None , special_requests:str= None)->PassengerDetailsResponse:
    logger.info(
        "Adding passenger details to hold",
        extra={
            "hold_id": hold_id,
            "passenger_name": passenger_name,
            "has_email": bool(passenger_email),
            "has_special_requests": bool(special_requests)
        }
    )
    
    passenger_details = {
        'passenger_name': passenger_name,
        'passenger_phone': passenger_phone,
        'passenger_email': passenger_email,
        'special_requests': special_requests
    }
    try: 
        updated_hold = add_passenger_to_hold(hold_id, passenger_details)
        
        logger.info(
            "Passenger details added successfully",
            extra={
                "hold_id": hold_id,
                "passenger": passenger_name,
                "phone": passenger_phone
            }
        )
        
        booking_summary = {
            'hold_id': hold_id,
            'cab_type': updated_hold['cab_details']['cab_type'],
            'price': updated_hold['price'],
            'pickup': updated_hold['pickup_location'],
            'drop': updated_hold['drop_location'],
            'departure_date': ensure_isoformat(updated_hold['departure_date']),
            'passenger': {
                'name': passenger_name,
                'phone': passenger_phone,
                'email': passenger_email
            }
        }

        
        return PassengerDetailsResponse(
            hold_id=hold_id,
            status=BookingStatus.PASSENGER_ADDED,
            passenger_name=passenger_name,
            passenger_phone=passenger_phone,
            passenger_email=passenger_email,
            special_requests=special_requests,
            ready_for_payment=True,
            expires_at=ensure_isoformat(updated_hold['expires_at']),
            booking_summary=booking_summary
        )
        
    except ValueError as e:
        logger.error(
            "Failed to add passenger details - validation error",
            extra={"hold_id": hold_id, "error": str(e)}
        )
        raise
    except Exception as e:
        logger.error(
            "Failed to add passenger details - unexpected error",
            extra={
                "hold_id": hold_id,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise ValueError(f"Failed to add passenger details: {str(e)}")

