from .mock_db import MOCK_CAB_DB , create_booking_hold ,  get_cab_by_id ,add_passenger_to_hold , get_passenger_details , is_hold_expired
from models.models import  SearchResponse , IndividualCabResponse , HoldCabResponse , BookingStatus  ,  PassengerDetailsResponse
from typing import List , Union
import logging
from datetime import datetime , timedelta , date
logger = logging.getLogger(__name__)


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
    
    logger.info(f"🔍 Searching cabs for route: '{pickup_lower}' → '{drop_lower}'")
    
    exact_match = MOCK_CAB_DB.get((pickup_lower, drop_lower), None)
    if exact_match:
        logger.info(f"✅ Exact match found in database")
        return SearchResponse(cabs=[
            IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
            for cab in exact_match
        ])
    
    logger.info(f"🔎 No exact match, trying fuzzy matching...")
    
    for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
        pickup_keywords = [w for w in pickup_key.split() if len(w) > 3]
        drop_keywords = [w for w in drop_key.split() if len(w) > 3]
        
        pickup_match = any(keyword in pickup_lower for keyword in pickup_keywords)
        drop_match = any(keyword in drop_lower for keyword in drop_keywords)
        
        if pickup_match and drop_match:
            logger.info(f"✅ Fuzzy match found: '{pickup_key}' → '{drop_key}'")
            return SearchResponse(cabs=[
                IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                for cab in cabs
            ])
    
    logger.info(f"🔎 Checking for intra-city routes...")
    
    cities = ["mumbai", "pune", "delhi", "bangalore", "hyderabad"]
    for city in cities:
        if city in pickup_lower and city in drop_lower:
            logger.info(f"✅ Intra-city route detected: {city}")
            for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
                if city in pickup_key and city in drop_key:
                    return SearchResponse(cabs=[
                        IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                        for cab in cabs
                    ])
    
    logger.info(f"⚠️ No specific route found, returning default cabs")
    logger.warning(f"Using default pricing - actual price may vary based on distance")

    return SearchResponse(cabs=[
        IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
        for cab in DEFAULT_CABS
    ])

def hold_cab(cab_id: str , pickup: str , drop: str , departure_date)->HoldCabResponse:
    logger.info(f"🔒 Creating hold for cab: {cab_id}")
    cab_details = get_cab_by_id(cab_id)
    if not cab_details:
        logger.error(f"❌ Cab not found: {cab_id}")
        raise ValueError(f"Invalid cab_id: {cab_id}. Cab not found in search results.")
    hold_data = create_booking_hold(cab_id, pickup, drop, departure_date)
    
    if not hold_data:
        logger.error(f"❌ Failed to create hold for cab: {cab_id}")
        raise ValueError("Failed to create booking hold")
    
    logger.info(f"✅ Hold created: {hold_data['hold_id']} (expires at {hold_data['expires_at']})")
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
    logger.info(f"Adding passenger details to hold : {hold_id}")
    passenger_details = {
        'passenger_name': passenger_name,
        'passenger_phone': passenger_phone,
        'passenger_email': passenger_email,
        'special_requests': special_requests
    }
    try: 
        updated_hold = add_passenger_to_hold(hold_id, passenger_details)
        logger.info(f"✅ Passenger details added: {passenger_name} ({passenger_phone})")
        
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
        logger.error(f"❌ Failed to add passenger details: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise ValueError(f"Failed to add passenger details: {str(e)}")

