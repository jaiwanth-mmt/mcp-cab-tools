import os
from typing import Optional
import httpx
from dotenv import load_dotenv


load_dotenv()

from models.models import LocationOption, ResolvedLocation
from services.logging_config import get_logger

logger = get_logger(__name__, service="geocoding")

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    logger.error("⚠️  GOOGLE_PLACES_API_KEY not found in environment variables")
    logger.error("⚠️  Please add your API key to the .env file")
    logger.error("⚠️  The server will not be able to fetch real location data")
   

PLACES_AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


async def geocode_location(query: str) -> list[LocationOption]:
    if not query or not query.strip():
        logger.warning("Received empty geocoding query")
        return []
    
    if not GOOGLE_PLACES_API_KEY:
        logger.error("GOOGLE_PLACES_API_KEY not configured")
        raise ValueError("Location service is not configured. Please contact administrator.")
    
    try:
        logger.debug(
            "Sending geocoding request to Google Places API",
            extra={"query": query}
        )
        
        params = {
            "input": query,
            "key": GOOGLE_PLACES_API_KEY,
            "types": "geocode|establishment",
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLACES_AUTOCOMPLETE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "OK":
            logger.warning(
                "Google Places API returned non-OK status",
                extra={"status": data.get("status"), "query": query}
            )
            return []
        
        predictions = data.get("predictions", [])
        logger.info(
            "Geocoding successful",
            extra={"query": query, "results_count": len(predictions)}
        )
        
        location_options = []
        for prediction in predictions:
            
            location_option = LocationOption(
                place_id=prediction["place_id"],
                formatted_address=prediction["description"],
                name=prediction.get("structured_formatting", {}).get("main_text", prediction["description"]),
                lat=0.0,
                lng=0.0
            )
            location_options.append(location_option)
        
        return location_options
    
    except httpx.TimeoutException:
        logger.error(
            "Geocoding request timed out",
            extra={"query": query, "timeout": "10s"}
        )
        return []
    except httpx.HTTPError as e:
        logger.error(
            "HTTP error during geocoding",
            extra={"query": query, "error": str(e)},
            exc_info=True
        )
        return []
    except Exception as e:
        logger.error(
            "Unexpected error during geocoding",
            extra={"query": query, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        return []


async def resolve_location_by_place_id(place_id: str) -> Optional[ResolvedLocation]:
    if not place_id:
        logger.warning("Received empty place_id for resolution")
        return None
    if not GOOGLE_PLACES_API_KEY:
        logger.error("GOOGLE_PLACES_API_KEY not configured for location resolution")
        return None
    try:
        logger.debug(
            "Resolving location details by place_id",
            extra={"place_id": place_id}
        )
        
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
            logger.warning(
                "Google Places Details API returned non-OK status",
                extra={"status": data.get("status"), "place_id": place_id}
            )
            return None
        
        result = data.get("result", {})
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        
        resolved_location = ResolvedLocation(
            original_query="",
            place_id=result.get("place_id", place_id),
            formatted_address=result.get("formatted_address", ""),
            name=result.get("name", ""),
            lat=location.get("lat", 0.0),
            lng=location.get("lng", 0.0),
        )
        
        logger.info(
            "Location resolved successfully",
            extra={
                "place_id": place_id,
                "location_name": resolved_location.name,  # Changed from 'name' to 'location_name'
                "coordinates": f"({resolved_location.lat}, {resolved_location.lng})"
            }
        )
        return resolved_location
    
    except httpx.TimeoutException:
        logger.error(
            "Location resolution timed out",
            extra={"place_id": place_id, "timeout": "10s"}
        )
        return None
    except httpx.HTTPError as e:
        logger.error(
            "HTTP error during location resolution",
            extra={"place_id": place_id, "error": str(e)},
            exc_info=True
        )
        return None
    except Exception as e:
        logger.error(
            "Unexpected error during location resolution",
            extra={"place_id": place_id, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        return None
