"""FastAPI Backend for Cab Booking Payment System"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

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
from services.logging_config import get_logger, setup_logging

# Setup logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"), use_stderr=True)
logger = get_logger(__name__, service="payment-backend")

app = FastAPI(
    title="Cab Booking Payment Backend",
    description="REST API for processing mock cab booking payments",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "cab-payment-backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/payment/initiate", response_model=PaymentInitiateResponse)
def initiate_payment(request: PaymentInitiateRequest):
    logger.info(
        "Payment initiation request",
        extra={"hold_id": request.hold_id}
    )
    
    try:
        hold = get_booking_hold(request.hold_id)
        if not hold:
            logger.error(
                "Hold not found",
                extra={"hold_id": request.hold_id}
            )
            raise HTTPException(status_code=404, detail=f"Hold not found: {request.hold_id}")
        
        if is_hold_expired(request.hold_id):
            logger.error(
                "Hold expired",
                extra={"hold_id": request.hold_id, "expires_at": hold.get('expires_at')}
            )
            raise HTTPException(status_code=400, detail="Hold has expired")
        
        if hold['status'] not in ['passenger_added', 'payment_pending', 'payment_success']:
            logger.error(
                "Invalid hold status for payment",
                extra={"hold_id": request.hold_id, "status": hold['status']}
            )
            raise HTTPException(
                status_code=400,
                detail=f"Passenger details must be added before payment. Current status: {hold['status']}"
            )
        
        amount = float(hold['price'])
        
        payment_session = create_payment_session(request.hold_id, amount)
        logger.info(
            "Payment session created",
            extra={
                "session_id": payment_session['session_id'],
                "hold_id": request.hold_id,
                "amount": amount
            }
        )
        
        return PaymentInitiateResponse(
            session_id=payment_session['session_id'],
            amount=amount,
            hold_id=request.hold_id,
            created_at=payment_session['created_at'].isoformat()
        )
        
    except ValueError as e:
        logger.error(
            "Payment initiation validation error",
            extra={"hold_id": request.hold_id, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error during payment initiation",
            extra={"hold_id": request.hold_id, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/payment/pay", response_model=PaymentProcessResponse)
def process_payment(request: PaymentProcessRequest):
    logger.info(
        "Payment processing request",
        extra={"session_id": request.session_id}
    )
    
    try:
        session = get_payment_session(request.session_id)
        if not session:
            logger.error(
                "Payment session not found",
                extra={"session_id": request.session_id}
            )
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        if session['status'] == 'completed':
            logger.warning(
                "Payment already completed",
                extra={"session_id": request.session_id}
            )
            raise HTTPException(status_code=400, detail="Payment already completed")
        
        if session['expires_at'] < datetime.now():
            logger.error(
                "Payment session expired",
                extra={"session_id": request.session_id, "expires_at": session['expires_at']}
            )
            raise HTTPException(status_code=400, detail="Payment session has expired")
        
        logger.debug(
            "Validating card details",
            extra={"session_id": request.session_id, "cardholder": request.cardholder_name}
        )
        
        card_valid, error_message = validate_card(
            request.card_number,
            request.cvv,
            request.expiry,
            request.cardholder_name
        )
        
        if not card_valid:
            logger.error(
                "Card validation failed",
                extra={"session_id": request.session_id, "error": error_message}
            )
            raise HTTPException(status_code=400, detail=error_message)
        
        card_clean = request.card_number.replace(" ", "").replace("-", "")
        card_last4 = card_clean[-4:]
        
        updated_session = update_payment_status(request.session_id, 'completed', card_last4)
        logger.info(
            "Payment completed successfully",
            extra={
                "session_id": request.session_id,
                "amount": session['amount'],
                "card_last4": card_last4
            }
        )
        
        return PaymentProcessResponse(
            success=True,
            message=f"Payment of ₹{session['amount']:.2f} completed successfully",
            session_id=request.session_id,
            card_last4=card_last4
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(
            "Payment processing validation error",
            extra={"session_id": request.session_id, "error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error during payment processing",
            extra={"session_id": request.session_id, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/payment/status/{session_id}", response_model=PaymentStatusResponse)
def get_payment_status(session_id: str):
    logger.info(
        "Payment status request",
        extra={"session_id": session_id}
    )
    
    try:
        session = get_payment_session(session_id)
        if not session:
            logger.error(
                "Payment session not found",
                extra={"session_id": session_id}
            )
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        logger.debug(
            "Payment status retrieved",
            extra={"session_id": session_id, "status": session['status']}
        )
        
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
        logger.error(
            "Unexpected error retrieving payment status",
            extra={"session_id": session_id, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/hold/{hold_id}", response_model=HoldDetailsResponse)
def get_hold_details(hold_id: str):
    logger.info(
        "Hold details request",
        extra={"hold_id": hold_id}
    )
    
    try:
        hold = get_booking_hold(hold_id)
        if not hold:
            logger.error(
                "Hold not found",
                extra={"hold_id": hold_id}
            )
            raise HTTPException(status_code=404, detail="Hold not found")
        
        passenger_details = hold.get('passenger_details', {})
        
        logger.debug(
            "Hold details retrieved",
            extra={"hold_id": hold_id, "status": hold.get('status')}
        )
        
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
        logger.error(
            "Unexpected error retrieving hold details",
            extra={"hold_id": hold_id, "error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Payment Backend Server...")
    logger.info("📍 Server will be available at: http://localhost:8000")
    logger.info("📖 API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
