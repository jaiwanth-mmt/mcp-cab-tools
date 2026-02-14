from .mock_db import MOCK_CAB_DB
from models.models import SearchRequest , SearchResponse , IndividualCabResponse
from typing import List
import logging

logger = logging.getLogger(__name__)


DEFAULT_CABS = [
    {"cab_type": "mini", "price": 300},
    {"cab_type": "sedan", "price": 500},
    {"cab_type": "suv", "price": 700},
    {"cab_type": "prime sedan", "price": 900},
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
            IndividualCabResponse(cab_type=cab["cab_type"], price=cab["price"]) 
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
                IndividualCabResponse(cab_type=cab["cab_type"], price=cab["price"]) 
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
                        IndividualCabResponse(cab_type=cab["cab_type"], price=cab["price"]) 
                        for cab in cabs
                    ])
    
    # Strategy 4: Default fallback - return standard cabs for any route
    logger.info(f"⚠️ No specific route found, returning default cabs")
    return SearchResponse(cabs=[
        IndividualCabResponse(cab_type=cab["cab_type"], price=cab["price"]) 
        for cab in DEFAULT_CABS
    ])
