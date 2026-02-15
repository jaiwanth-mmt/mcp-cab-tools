from datetime import date , datetime

from enum import Enum
from typing import  Any , Optional
from pydantic import BaseModel , Field, field_validator , model_serializer
import re 
class TripType(str , Enum):
    OW = "one way"
    RT = "round trip"
    HR = "Hourly rental"
    AT = "Airport Transfer"


class SearchRequest(BaseModel):
    pickup : str = Field(... ,min_length = 1 ,description="Pikcup location")
    drop: str = Field(...,min_length=1, description='Drop Location')
    trip_type : TripType = Field(description="Type of trip")
    departure_date: date = Field(description="Date of Journey" , examples=["23-05-2004"])

    @field_validator("departure_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, date):
            return v

        if isinstance(v, str):
           
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    pass

        raise ValueError(
            "departure_date must be in dd-MM-yyyy or yyyy-MM-dd format"
        )

    @field_validator("pickup", "drop")
    @classmethod
    def normalize_location(cls, v: str):
        return v.strip().lower()
        
class IndividualCabResponse(BaseModel):
    cab_id: str = Field(description="unique identifer for the cab")
    cab_type: str = Field(description="Type of car")
    price: int = Field(description="price of cab")    

class SearchResponse(BaseModel):
    cabs: list[IndividualCabResponse] = Field(description="list of available cabs")
     
class LocationOption(BaseModel):
    place_id: str = Field(description="unique identifer for the place")
    formatted_address: str = Field(description="full formatted address")
    name: str = Field(description='Name of the place')
    lat: float = Field(description='Latitude')
    lng: float = Field(description='Longitude')
    


class ResolvedLocation(BaseModel):
    original_query: str
    place_id: str
    formatted_address: str
    name: str
    lat: float
    long: float

class BookingStatus(str , Enum):
    HELD = "held"
    PASSENGER_ADDED = "passenger_added"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_SUCCESS = "payment_success"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class HoldCabRequest(BaseModel):
    cab_id: str = Field(..., description="Unique cab identifier from search results")
    departure_date: date = Field(..., description="Date of journey")
    pickup: str = Field(..., min_length=1, description="Pickup location")
    drop: str = Field(..., min_length=1, description="Drop location")

    @field_validator("departure_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    pass
        raise ValueError("departure_date must be in dd-MM-yyyy or yyyy-MM-dd format")
    
    @field_validator("departure_date")
    @classmethod
    def validate_future_date(cls, v):
        if v < date.today():
            raise ValueError("departure_date must be today or a future date")
        return v

class HoldCabResponse(BaseModel):
    hold_id: str = Field(description="Unique hold identifier")
    cab_id: str = Field(description="Cab identifier")
    status: BookingStatus = Field(description="Current booking status")
    expires_at: str = Field(description="Hold expiration time (ISO 8601 format)")
    cab_details: dict = Field(description="Cab information")
    price: int = Field(description="Total price")
    pickup_location: str = Field(description="Pickup location")
    drop_location: str = Field(description="Drop location")
    departure_date: str = Field(description="Journey date (ISO 8601 format)")
    created_at: str = Field(description="Hold creation time (ISO 8601 format)")

