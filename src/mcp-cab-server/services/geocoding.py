import os
import logging
from typing import Optional
import httpx
from dotenv import load_dotenv


load_dotenv()

from models.models import LocationOption, ResolvedLocation

logger = logging.getLogger(__name__)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    logger.error("⚠️  GOOGLE_PLACES_API_KEY not found in environment variables")
    logger.error("⚠️  Please add your API key to the .env file")
    logger.error("⚠️  The server will not be able to fetch real location data")
   

# Google Places API endpoints
PLACES_AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


async def geocode_location(query: str) -> list[LocationOption]:
    """
    Use Google Places Autocomplete API to get location suggestions.
    
    Args:
        query: User's search query for location
        
    Returns:
        List of LocationOption objects with place suggestions
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to geocode_location")
        return []
    
    if not GOOGLE_PLACES_API_KEY:
        logger.error("Cannot geocode location - GOOGLE_PLACES_API_KEY not configured")
        logger.error("Please add your API key to the .env file")
        return []
    
    try:
        params = {
            "input": query,
            "key": GOOGLE_PLACES_API_KEY,
            "types": "geocode|establishment",  # Allow both addresses and places
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLACES_AUTOCOMPLETE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "OK":
            logger.warning(f"Google Places API returned status: {data.get('status')}")
            return []
        
        predictions = data.get("predictions", [])
        logger.info(f"Found {len(predictions)} location suggestions for query: '{query}'")
        
        
        location_options = []
        for prediction in predictions:
            
            location_option = LocationOption(
                place_id=prediction["place_id"],
                formatted_address=prediction["description"],
                name=prediction.get("structured_formatting", {}).get("main_text", prediction["description"]),
                lat=0.0,  # Will be populated when place is selected
                lng=0.0   # Will be populated when place is selected
            )
            location_options.append(location_option)
        
        return location_options
    
    except httpx.TimeoutException:
        logger.error(f"Timeout while geocoding location: {query}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while geocoding location: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in geocode_location: {e}")
        return []


async def resolve_location_by_place_id(place_id: str) -> Optional[ResolvedLocation]:
    """
    Use Google Places Details API to get complete location details including coordinates.
    
    Args:
        place_id: Google Places place_id from autocomplete selection
        
    Returns:
        ResolvedLocation with complete place details including coordinates
    """
    if not place_id:
        logger.warning("Empty place_id provided to resolve_location_by_place_id")
        return None
    
    try:
        params = {
            "place_id": place_id,
            "key": GOOGLE_PLACES_API_KEY,
            "fields": "place_id,formatted_address,name,geometry",
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLACES_DETAILS_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "OK":
            logger.warning(f"Google Places Details API returned status: {data.get('status')}")
            return None
        
        result = data.get("result", {})
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        
        resolved_location = ResolvedLocation(
            original_query="",  # Not available in this context
            place_id=result.get("place_id", place_id),
            formatted_address=result.get("formatted_address", ""),
            name=result.get("name", ""),
            lat=location.get("lat", 0.0),
            long=location.get("lng", 0.0),
        )
        
        logger.info(f"✅ Resolved location: {resolved_location.name} at ({resolved_location.lat}, {resolved_location.long})")
        return resolved_location
    
    except httpx.TimeoutException:
        logger.error(f"Timeout while resolving place_id: {place_id}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while resolving place_id: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in resolve_location_by_place_id: {e}")
        return None
