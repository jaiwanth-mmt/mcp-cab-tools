from .mock_db import MOCK_CAB_DB , create_booking_hold ,  get_cab_by_id  
from models.models import SearchRequest , SearchResponse , IndividualCabResponse , HoldCabResponse , BookingStatus
from typing import List
import logging
from datetime import datetime , timedelta
logger = logging.getLogger(__name__)


DEFAULT_CABS = [
    {"cab_id": "DEF_CAB_MINI", "cab_type": "mini", "price": 300},
    {"cab_id": "DEF_CAB_SEDAN", "cab_type": "sedan", "price": 500},
    {"cab_id": "DEF_CAB_SUV", "cab_type": "suv", "price": 700},
    {"cab_id": "DEF_CAB_PRIME_SEDAN", "cab_type": "prime sedan", "price": 900},
]

def get_available_cabs(pickup: str, drop: str) -> SearchResponse:
    """
    Get available cabs between pickup and drop locations.
    Uses fuzzy matching with fallback to ensure results are always returned.
    """
    pickup_lower = pickup.lower()
    drop_lower = drop.lower()
    
    logger.info(f"🔍 Searching cabs for route: '{pickup_lower}' → '{drop_lower}'")
    
    # Strategy 1: Try exact match first
    exact_match = MOCK_CAB_DB.get((pickup_lower, drop_lower), None)
    if exact_match:
        logger.info(f"✅ Exact match found in database")
        return SearchResponse(cabs=[
            IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
            for cab in exact_match
        ])
    
    # Strategy 2: Fuzzy matching - check if keywords exist in location names
    logger.info(f"🔎 No exact match, trying fuzzy matching...")
    
    for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
        # Extract significant words (ignore common words)
        pickup_keywords = [w for w in pickup_key.split() if len(w) > 3]
        drop_keywords = [w for w in drop_key.split() if len(w) > 3]
        
        # Check if any significant keyword from the key exists in the actual location name
        pickup_match = any(keyword in pickup_lower for keyword in pickup_keywords)
        drop_match = any(keyword in drop_lower for keyword in drop_keywords)
        
        if pickup_match and drop_match:
            logger.info(f"✅ Fuzzy match found: '{pickup_key}' → '{drop_key}'")
            return SearchResponse(cabs=[
                IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                for cab in cabs
            ])
    
    # Strategy 3: Check if both locations contain same city (intra-city travel)
    logger.info(f"🔎 Checking for intra-city routes...")
    
    cities = ["mumbai", "pune", "delhi", "bangalore", "hyderabad"]
    for city in cities:
        if city in pickup_lower and city in drop_lower:
            logger.info(f"✅ Intra-city route detected: {city}")
            # Return city-specific cabs or default
            for (pickup_key, drop_key), cabs in MOCK_CAB_DB.items():
                if city in pickup_key and city in drop_key:
                    return SearchResponse(cabs=[
                        IndividualCabResponse(cab_id=cab["cab_id"], cab_type=cab["cab_type"], price=cab["price"]) 
                        for cab in cabs
                    ])
    
    
    logger.info(f"⚠️ No specific route found, returning default cabs")
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
        expires_at=hold_data['expires_at'],
        cab_details=hold_data['cab_details'],
        price=hold_data['price'],
        pickup_location=hold_data['pickup_location'],
        drop_location=hold_data['drop_location'],
        departure_date=hold_data['departure_date'],
        created_at=hold_data['created_at']
    )