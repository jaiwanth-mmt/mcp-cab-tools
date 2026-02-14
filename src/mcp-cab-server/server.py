from email import message
import os
from dotenv import load_dotenv
load_dotenv()
from fastmcp import FastMCP , Context
from models.models import  SearchRequest, SearchResponse 
import logging
from services.helper import get_available_cabs
from services.geocoding import geocode_location , resolve_location_by_place_id

# Load environment variables from .env file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("cab-server")



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
    logger.info(f"✅ User selected {location_type}: {location.name}")
    return location, None



@mcp.tool(name="Search_cabs" , description="Cabs to search")
async def search_cabs(ctx:Context , input: SearchRequest)->SearchResponse:
    logger.info(f"🔍 Cab search request - Pickup: {input.pickup}, Drop: {input.drop}")
    pickup_location , pickup_error = await get_location_with_disambiguation(ctx , input.pickup , "pickup")
    if pickup_error:
        return SearchResponse(cabs = [])
    drop_location , drop_error = await get_location_with_disambiguation(ctx , input.drop , "drop")
    if drop_error:
        return SearchResponse(cabs = [])
    logger.info(f"✅ Locations resolved - Pickup: {pickup_location.name}, Drop: {drop_location.name}")
    available_cabs = get_available_cabs(pickup_location.name.lower(), drop_location.name.lower())
    return available_cabs


    


  



if __name__ == "__main__":
    mcp.run()