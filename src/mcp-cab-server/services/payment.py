from datetime import datetime
from urllib.parse import quote
from services.logging_config import get_logger
from models.models import (
    PaymentOrderResponse,
    PaymentVerifyResponse,
    ConfirmBookingResponse,
    DriverDetails,
    BookingStatus,
    PaymentStatus
)
from services.mock_db import (
    get_booking_hold,
    create_payment_session,
    get_payment_session,
    get_payment_by_hold,
    assign_driver_to_booking,
    confirm_booking_final,
    is_hold_expired
)

logger = get_logger(__name__, service="payment")

FRONTEND_URL = "http://localhost:8501"


def ensure_isoformat(value) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def create_payment_order_internal(hold_id: str) -> PaymentOrderResponse:
    logger.info(
        "Creating payment order",
        extra={"hold_id": hold_id}
    )
    
    hold = get_booking_hold(hold_id)
    if not hold:
        logger.error(
            "Hold not found for payment order",
            extra={"hold_id": hold_id}
        )
        raise ValueError(f"Hold not found: {hold_id}")
    
    if is_hold_expired(hold_id):
        logger.error(
            "Hold expired, cannot create payment order",
            extra={"hold_id": hold_id, "expires_at": hold.get('expires_at')}
        )
        raise ValueError(f"Hold has expired")
    
    if hold['status'] not in ['passenger_added', 'payment_pending']:
        logger.error(
            "Hold not ready for payment",
            extra={"hold_id": hold_id, "status": hold['status']}
        )
        raise ValueError(
            f"Cannot create payment order. Passenger details must be added first. "
            f"Current status: {hold['status']}"
        )
    
    amount = float(hold['price'])
    
    try:
        payment_session = create_payment_session(hold_id, amount)
        logger.info(
            "Payment session created successfully",
            extra={
                "session_id": payment_session['session_id'],
                "hold_id": hold_id,
                "amount": amount
            }
        )
    except ValueError as e:
        logger.error(
            "Failed to create payment session",
            extra={"hold_id": hold_id, "error": str(e)}
        )
        raise
    
    session_id = payment_session['session_id']
    pickup_encoded = quote(hold['pickup_location'])
    drop_encoded = quote(hold['drop_location'])
    
    payment_url = (
        f"{FRONTEND_URL}?"
        f"session_id={session_id}&"
        f"amount={amount}&"
        f"hold_id={hold_id}&"
        f"pickup={pickup_encoded}&"
        f"drop={drop_encoded}"
    )
    
    logger.debug(
        "Payment URL generated",
        extra={"session_id": session_id, "url_length": len(payment_url)}
    )
    
    return PaymentOrderResponse(
        session_id=session_id,
        payment_url=payment_url,
        amount=amount,
        hold_id=hold_id,
        expires_at=ensure_isoformat(payment_session['expires_at']),
        created_at=ensure_isoformat(payment_session['created_at'])
    )


def get_payment_status_internal(session_id: str) -> PaymentVerifyResponse:
    logger.info(
        "Checking payment status",
        extra={"session_id": session_id}
    )
    
    payment_session = get_payment_session(session_id)
    if not payment_session:
        logger.error(
            "Payment session not found",
            extra={"session_id": session_id}
        )
        raise ValueError(f"Payment session not found: {session_id}")
    
    status_map = {
        'pending': PaymentStatus.PENDING,
        'completed': PaymentStatus.COMPLETED,
        'failed': PaymentStatus.FAILED
    }
    status = status_map.get(payment_session['status'], PaymentStatus.PENDING)
    
    logger.info(
        "Payment status retrieved",
        extra={
            "session_id": session_id,
            "status": status.value,
            "amount": payment_session['amount'],
            "hold_id": payment_session['hold_id']
        }
    )
    
    return PaymentVerifyResponse(
        session_id=session_id,
        status=status,
        amount=payment_session['amount'],
        hold_id=payment_session['hold_id'],
        created_at=ensure_isoformat(payment_session['created_at']),
        completed_at=ensure_isoformat(payment_session['completed_at']) if payment_session['completed_at'] else None,
        card_last4=payment_session.get('card_last4')
    )


def confirm_booking_internal(hold_id: str) -> ConfirmBookingResponse:
    logger.info(
        "Starting booking confirmation",
        extra={"hold_id": hold_id}
    )
    
    hold = get_booking_hold(hold_id)
    if not hold:
        logger.error(
            "Hold not found for confirmation",
            extra={"hold_id": hold_id}
        )
        raise ValueError(f"Hold not found: {hold_id}")
    
    if is_hold_expired(hold_id):
        logger.error(
            "Hold expired, cannot confirm booking",
            extra={"hold_id": hold_id, "expires_at": hold.get('expires_at')}
        )
        raise ValueError(f"Hold has expired")
    
    payment = get_payment_by_hold(hold_id)
    if not payment:
        logger.error(
            "No payment found for hold",
            extra={"hold_id": hold_id, "hold_status": hold['status']}
        )
        raise ValueError(
            f"Payment not completed for this booking. "
            f"Please complete payment before confirming. "
            f"Current status: {hold['status']}"
        )
    if payment['completed_at'] and hold['expires_at']:
        if payment['completed_at'] > hold['expires_at']:
            logger.error(
                "Payment completed after hold expiry",
                extra={
                    "hold_id": hold_id,
                    "payment_time": str(payment['completed_at']),
                    "expiry_time": str(hold['expires_at'])
                }
            )
            raise ValueError("Payment was completed after hold expired. Cannot confirm.")
    
    if hold['status'] not in ['payment_success', 'confirmed']:
        logger.error(
            "Invalid hold status for confirmation",
            extra={"hold_id": hold_id, "status": hold['status']}
        )
        raise ValueError(
            f"Cannot confirm booking. Current status: {hold['status']}. "
            f"Payment must be completed first."
        )
    
    if hold['status'] == 'confirmed' and 'booking_id' in hold:
        logger.info(
            "Booking already confirmed, returning existing details",
            extra={"hold_id": hold_id, "booking_id": hold['booking_id']}
        )
        driver = hold.get('driver', {})
        
        return ConfirmBookingResponse(
            booking_id=hold['booking_id'],
            hold_id=hold_id,
            status=BookingStatus.CONFIRMED,
            driver=DriverDetails(**driver),
            booking_summary=_build_booking_summary(hold),
            confirmed_at=ensure_isoformat(hold.get('confirmed_at', datetime.now()))
        )
    
    try:
        driver = assign_driver_to_booking(hold_id)
        logger.info(
            "Driver assigned to booking",
            extra={
                "hold_id": hold_id,
                "driver_name": driver['name'],
                "vehicle": driver['vehicle_number']
            }
        )
    except ValueError as e:
        logger.error(
            "Failed to assign driver",
            extra={"hold_id": hold_id, "error": str(e)}
        )
        raise
    
    try:
        confirmed_hold = confirm_booking_final(hold_id, driver)
        logger.info(
            "Booking confirmed successfully",
            extra={
                "booking_id": confirmed_hold['booking_id'],
                "hold_id": hold_id,
                "driver": driver['name']
            }
        )
    except ValueError as e:
        logger.error(
            "Failed to finalize booking confirmation",
            extra={"hold_id": hold_id, "error": str(e)}
        )
        raise
    
    return ConfirmBookingResponse(
        booking_id=confirmed_hold['booking_id'],
        hold_id=hold_id,
        status=BookingStatus.CONFIRMED,
        driver=DriverDetails(
            name=driver['name'],
            phone=driver['phone'],
            vehicle_number=driver['vehicle_number'],
            vehicle_model=driver['vehicle_model'],
            rating=driver['rating']
        ),
        booking_summary=_build_booking_summary(confirmed_hold),
        confirmed_at=ensure_isoformat(confirmed_hold['confirmed_at'])
    )


def _build_booking_summary(hold: dict) -> dict:
    passenger_details = hold.get('passenger_details', {})
    
    summary = {
        'booking_id': hold.get('booking_id', 'N/A'),
        'hold_id': hold['hold_id'],
        'cab_type': hold['cab_details']['cab_type'],
        'price': hold['price'],
        'pickup': hold['pickup_location'],
        'drop': hold['drop_location'],
        'departure_date': ensure_isoformat(hold['departure_date']),
        'passenger': {
            'name': passenger_details.get('passenger_name', 'N/A'),
            'phone': passenger_details.get('passenger_phone', 'N/A'),
            'email': passenger_details.get('passenger_email')
        },
        'status': hold['status'],
        'created_at': ensure_isoformat(hold['created_at']),
        'confirmed_at': ensure_isoformat(hold.get('confirmed_at'))
    }
    
    if 'driver' in hold:
        summary['driver'] = hold['driver']
    
    return summary
