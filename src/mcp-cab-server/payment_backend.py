"""
FastAPI Backend for Cab Booking Payment System
Provides REST API endpoints for payment processing with mock card validation.
"""

import sys
import os

# Add current directory to path for imports (where models, services are located)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional
import logging

# Import local modules
from models.models import (
    PaymentProcessRequest,
    PaymentProcessResponse,
    PaymentStatus
)
from services.mock_db import (
    get_booking_hold,
    create_payment_session,
    get_payment_session,
    update_payment_status,
    is_hold_expired
)
from services.card_validator import validate_card

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cab Booking Payment Backend",
    description="REST API for processing mock cab booking payments",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== REQUEST/RESPONSE MODELS ====================

class PaymentInitiateRequest(BaseModel):
    hold_id: str = Field(..., description="Hold ID to create payment for")


class PaymentInitiateResponse(BaseModel):
    session_id: str = Field(description="Payment session ID")
    amount: float = Field(description="Payment amount")
    hold_id: str = Field(description="Associated hold ID")
    created_at: str = Field(description="Creation timestamp")


class PaymentStatusResponse(BaseModel):
    session_id: str = Field(description="Payment session ID")
    status: str = Field(description="Payment status")
    amount: float = Field(description="Payment amount")
    hold_id: str = Field(description="Associated hold ID")
    created_at: str = Field(description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    card_last4: Optional[str] = Field(None, description="Last 4 digits of card")


class HoldDetailsResponse(BaseModel):
    hold_id: str
    cab_type: str
    pickup: str
    drop: str
    departure_date: str
    price: float
    passenger_name: Optional[str] = None


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "cab-payment-backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/payment/initiate", response_model=PaymentInitiateResponse)
def initiate_payment(request: PaymentInitiateRequest):
    """
    Create a new payment session for a booking hold.
    
    This endpoint validates the hold and creates a payment session
    that can be used to process payment.
    """
    logger.info(f"💳 Payment initiation request for hold: {request.hold_id}")
    
    try:
        # Get hold details
        hold = get_booking_hold(request.hold_id)
        if not hold:
            logger.error(f"❌ Hold not found: {request.hold_id}")
            raise HTTPException(status_code=404, detail=f"Hold not found: {request.hold_id}")
        
        # Check if hold expired
        if is_hold_expired(request.hold_id):
            logger.error(f"❌ Hold expired: {request.hold_id}")
            raise HTTPException(status_code=400, detail="Hold has expired")
        
        # Check if passenger details added
        if hold['status'] not in ['passenger_added', 'payment_pending', 'payment_success']:
            logger.error(f"❌ Invalid hold status: {hold['status']}")
            raise HTTPException(
                status_code=400,
                detail=f"Passenger details must be added before payment. Current status: {hold['status']}"
            )
        
        # Get amount
        amount = float(hold['price'])
        
        # Create payment session
        payment_session = create_payment_session(request.hold_id, amount)
        logger.info(f"✅ Payment session created: {payment_session['session_id']}")
        
        return PaymentInitiateResponse(
            session_id=payment_session['session_id'],
            amount=amount,
            hold_id=request.hold_id,
            created_at=payment_session['created_at'].isoformat()
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/payment/pay", response_model=PaymentProcessResponse)
def process_payment(request: PaymentProcessRequest):
    """
    Process a payment with card details.
    
    This endpoint validates the card details using realistic validation
    (Luhn algorithm, expiry checks, etc.) and marks the payment as completed.
    """
    logger.info(f"💳 Payment processing request for session: {request.session_id}")
    
    try:
        # Get payment session
        session = get_payment_session(request.session_id)
        if not session:
            logger.error(f"❌ Payment session not found: {request.session_id}")
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        # Check if already completed
        if session['status'] == 'completed':
            logger.warning(f"⚠️ Payment already completed: {request.session_id}")
            raise HTTPException(status_code=400, detail="Payment already completed")
        
        # Check if session expired
        if session['expires_at'] < datetime.now():
            logger.error(f"❌ Payment session expired: {request.session_id}")
            raise HTTPException(status_code=400, detail="Payment session has expired")
        
        # Validate card
        card_valid, error_message = validate_card(
            request.card_number,
            request.cvv,
            request.expiry,
            request.cardholder_name
        )
        
        if not card_valid:
            logger.error(f"❌ Card validation failed: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        # Get last 4 digits
        card_clean = request.card_number.replace(" ", "").replace("-", "")
        card_last4 = card_clean[-4:]
        
        # Update payment status
        updated_session = update_payment_status(request.session_id, 'completed', card_last4)
        logger.info(f"✅ Payment completed successfully: {request.session_id}")
        
        return PaymentProcessResponse(
            success=True,
            message=f"Payment of ₹{session['amount']:.2f} completed successfully",
            session_id=request.session_id,
            card_last4=card_last4
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/payment/status/{session_id}", response_model=PaymentStatusResponse)
def get_payment_status(session_id: str):
    """
    Get payment session status.
    
    Returns the current status of a payment session including
    whether it's pending, completed, or failed.
    """
    logger.info(f"🔍 Payment status request for session: {session_id}")
    
    try:
        session = get_payment_session(session_id)
        if not session:
            logger.error(f"❌ Payment session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        return PaymentStatusResponse(
            session_id=session_id,
            status=session['status'],
            amount=session['amount'],
            hold_id=session['hold_id'],
            created_at=session['created_at'].isoformat(),
            completed_at=session['completed_at'].isoformat() if session['completed_at'] else None,
            card_last4=session.get('card_last4')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/hold/{hold_id}", response_model=HoldDetailsResponse)
def get_hold_details(hold_id: str):
    """
    Get booking hold details for display in payment UI.
    
    Returns basic hold information needed to show booking summary
    on the payment page.
    """
    logger.info(f"📋 Hold details request for: {hold_id}")
    
    try:
        hold = get_booking_hold(hold_id)
        if not hold:
            logger.error(f"❌ Hold not found: {hold_id}")
            raise HTTPException(status_code=404, detail="Hold not found")
        
        passenger_details = hold.get('passenger_details', {})
        
        return HoldDetailsResponse(
            hold_id=hold['hold_id'],
            cab_type=hold['cab_details']['cab_type'],
            pickup=hold['pickup_location'],
            drop=hold['drop_location'],
            departure_date=hold['departure_date'].isoformat() if hasattr(hold['departure_date'], 'isoformat') else str(hold['departure_date']),
            price=float(hold['price']),
            passenger_name=passenger_details.get('passenger_name')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Payment Backend Server...")
    logger.info("📍 Server will be available at: http://localhost:8000")
    logger.info("📖 API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
