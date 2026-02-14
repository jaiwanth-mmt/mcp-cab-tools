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

@mcp.tool(name="Search_cabs" , description="Cabs to search")
async def search_cabs(ctx:Context , input: SearchRequest)->SearchResponse:
    logger.info(f"🔍 Cab search request - Pickup: {input.pickup}, Drop: {input.drop}")
    
    
    logger.info(f"📍 Geocoding pickup location: {input.pickup}")
    pickup_results = await geocode_location(input.pickup)
    if not pickup_results:
        return SearchRequest(cabs = [] , message="No cabs for this pickup location")
    if len(pickup_results) > 1:
        logger.info(f"Multiple Pickup locations detected {len(pickup_results)}, requesting user selection")
        options_dict = {
            loc.place_id: {
                "title":f"{loc.name} - {loc.formatted_address}"
            }
            for loc in pickup_results
        }
        
        response = await ctx.elicit(
            message=f"🚕 Found {len(pickup_results)} locations for '{input.pickup}'. Please select the pickup location:",
            response_type=options_dict
        )
        place_id = response.data
        if place_id:
            pickup_location = await resolve_location_by_place_id(place_id)
        else:
            return SearchRequest(cabs = [] , message="No pickup location selected")
    else:
        loc = pickup_results[0]
        pickup_location = await resolve_location_by_place_id(loc.place_id)
        logger.info(f"✅ Single pickup location found: {pickup_location.name}")
    
    logger.info(f"📍 Geocoding drop location: {input.drop}")
    drop_results = await geocode_location(input.drop)
    if len(drop_results) > 1:
        logger.info(f"Multiple Drop locations detected {len(drop_results)}, requesting user selection")
        options_dict = {
            loc.place_id: {
                "title":f"{loc.name} - {loc.formatted_address}"
            }
            for loc in drop_results
        }
        response = await ctx.elicit(
            message=f"🚕 Found {len(drop_results)} locations for '{input.drop}'. Please select the drop location:",
            response_type=options_dict
        )

        place_id = response.data
        if place_id:
            drop_location = await resolve_location_by_place_id(place_id)
        else:
            return SearchRequest(cabs = [] , message="No drop location selected")
    else:
        loc = drop_results[0]
        drop_location = await resolve_location_by_place_id(loc.place_id)
        logger.info(f"✅ Single drop location found: {drop_location.name}")
    
    available_cabs = get_available_cabs(pickup_location.name.lower() , drop_location.name.lower())
    return available_cabs


  



if __name__ == "__main__":
    mcp.run()