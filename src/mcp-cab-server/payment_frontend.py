"""
Streamlit Frontend for Cab Booking Payment System
User-facing payment form for completing mock payments with realistic validation.
"""

import streamlit as st
import httpx
from urllib.parse import unquote
import re

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="Cab Booking Payment",
    page_icon="🚕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://localhost:8000"

# ==================== STYLING ====================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
    }
    .payment-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== VALIDATION FUNCTIONS ====================

def format_card_number(card_number: str) -> str:
    """Format card number with spaces every 4 digits"""
    digits = re.sub(r'\D', '', card_number)
    return ' '.join([digits[i:i+4] for i in range(0, len(digits), 4)])


def validate_card_number_client(card_number: str) -> tuple[bool, str]:
    """Client-side card number validation"""
    card_clean = card_number.replace(" ", "").replace("-", "")
    
    if not card_clean:
        return False, "Card number is required"
    
    if not card_clean.isdigit():
        return False, "Card number must contain only digits"
    
    if len(card_clean) < 13 or len(card_clean) > 19:
        return False, "Card number must be 13-19 digits"
    
    return True, ""


def validate_cvv_client(cvv: str) -> tuple[bool, str]:
    """Client-side CVV validation"""
    if not cvv:
        return False, "CVV is required"
    
    if not cvv.isdigit():
        return False, "CVV must contain only digits"
    
    if len(cvv) < 3 or len(cvv) > 4:
        return False, "CVV must be 3 or 4 digits"
    
    return True, ""


def validate_expiry_client(expiry: str) -> tuple[bool, str]:
    """Client-side expiry validation"""
    if not expiry:
        return False, "Expiry date is required"
    
    if "/" not in expiry:
        return False, "Expiry must be in MM/YY format"
    
    parts = expiry.split("/")
    if len(parts) != 2:
        return False, "Expiry must be in MM/YY format"
    
    month, year = parts
    
    if len(month) != 2 or len(year) != 2:
        return False, "Expiry must be in MM/YY format"
    
    if not month.isdigit() or not year.isdigit():
        return False, "Expiry must contain only digits"
    
    month_int = int(month)
    if month_int < 1 or month_int > 12:
        return False, "Invalid month (01-12)"
    
    return True, ""


def validate_name_client(name: str) -> tuple[bool, str]:
    """Client-side name validation"""
    if not name or len(name.strip()) == 0:
        return False, "Cardholder name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    return True, ""


# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown('<h1 class="main-header">🚕 Secure Payment Gateway</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get URL parameters
    query_params = st.query_params
    session_id = query_params.get("session_id", "")
    amount_str = query_params.get("amount", "0")
    hold_id = query_params.get("hold_id", "")
    pickup = unquote(query_params.get("pickup", ""))
    drop = unquote(query_params.get("drop", ""))
    
    # Validate required parameters
    if not session_id or not hold_id:
        st.error("❌ Invalid payment link - missing required parameters")
        st.info("Please use the payment link provided by the booking system.")
        return
    
    try:
        amount = float(amount_str)
    except ValueError:
        st.error("❌ Invalid amount specified")
        return
    
    # Check payment status first
    try:
        with httpx.Client(timeout=10.0) as client:
            status_response = client.get(f"{BACKEND_URL}/api/payment/status/{session_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if status_data["status"] == "completed":
                    # Payment already completed
                    st.success("✅ Payment Already Completed!")
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write(f"**Transaction ID:** `{session_id}`")
                    st.write(f"**Amount Paid:** ₹{amount:.2f}")
                    if status_data.get("card_last4"):
                        st.write(f"**Card Used:** •••• {status_data['card_last4']}")
                    st.write(f"**Completed At:** {status_data.get('completed_at', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.info("You can now close this window and confirm your booking.")
                    return
    except Exception as e:
        st.warning(f"Unable to verify payment status: {str(e)}")
    
    # Fetch hold details
    hold_details = None
    try:
        with httpx.Client(timeout=10.0) as client:
            hold_response = client.get(f"{BACKEND_URL}/api/hold/{hold_id}")
            if hold_response.status_code == 200:
                hold_details = hold_response.json()
    except Exception as e:
        st.warning(f"Unable to fetch booking details: {str(e)}")
    
    # Display booking summary
    st.subheader("📋 Booking Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Amount to Pay", f"₹{amount:.2f}")
    with col2:
        st.metric("Status", "Pending Payment")
    
    if hold_details:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.write(f"**Cab Type:** {hold_details.get('cab_type', 'N/A')}")
        st.write(f"**Route:** {hold_details.get('pickup', pickup)} → {hold_details.get('drop', drop)}")
        st.write(f"**Date:** {hold_details.get('departure_date', 'N/A')}")
        if hold_details.get('passenger_name'):
            st.write(f"**Passenger:** {hold_details['passenger_name']}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"**Route:** {pickup} → {drop}")
    
    st.markdown("---")
    st.subheader("💳 Payment Information")
    
    # Payment form
    with st.form("payment_form", clear_on_submit=False):
        # Card number
        card_number = st.text_input(
            "Card Number",
            placeholder="4111 1111 1111 1111",
            max_chars=19,
            help="Enter your 16-digit card number"
        )
        
        # Expiry and CVV
        col1, col2 = st.columns(2)
        with col1:
            expiry = st.text_input(
                "Expiry Date",
                placeholder="MM/YY",
                max_chars=5,
                help="Format: MM/YY (e.g., 12/25)"
            )
        with col2:
            cvv = st.text_input(
                "CVV",
                placeholder="123",
                max_chars=4,
                type="password",
                help="3 or 4 digit security code"
            )
        
        # Cardholder name
        cardholder_name = st.text_input(
            "Cardholder Name",
            placeholder="JOHN DOE",
            help="Name as it appears on the card"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            "💳 Pay Now",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            # Validate inputs
            errors = []
            
            valid, msg = validate_card_number_client(card_number)
            if not valid:
                errors.append(msg)
            
            valid, msg = validate_cvv_client(cvv)
            if not valid:
                errors.append(msg)
            
            valid, msg = validate_expiry_client(expiry)
            if not valid:
                errors.append(msg)
            
            valid, msg = validate_name_client(cardholder_name)
            if not valid:
                errors.append(msg)
            
            # Display errors or process payment
            if errors:
                st.error("❌ Please fix the following errors:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Process payment
                with st.spinner("🔄 Processing payment..."):
                    try:
                        # Clean card number
                        card_clean = card_number.replace(" ", "").replace("-", "")
                        
                        # Prepare payload
                        payload = {
                            "session_id": session_id,
                            "card_number": card_clean,
                            "cvv": cvv,
                            "expiry": expiry,
                            "cardholder_name": cardholder_name
                        }
                        
                        # Call backend
                        with httpx.Client(timeout=30.0) as client:
                            response = client.post(
                                f"{BACKEND_URL}/api/payment/pay",
                                json=payload
                            )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.write(f"**Transaction ID:** `{session_id}`")
                            st.write(f"**Amount Paid:** ₹{amount:.2f}")
                            if result.get('card_last4'):
                                st.write(f"**Card Used:** •••• {result['card_last4']}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.info("✅ Payment successful! You can now proceed to confirm your booking.")
                            st.info("💡 You can close this window and use the MCP chat to confirm your booking.")
                        else:
                            error_data = response.json()
                            error_detail = error_data.get('detail', 'Unknown error')
                            st.error(f"❌ Payment failed: {error_detail}")
                    
                    except httpx.ConnectError:
                        st.error("❌ Unable to connect to payment server.")
                        st.error("Please ensure the backend server is running on port 8000.")
                    except httpx.TimeoutException:
                        st.error("❌ Payment request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Payment processing error: {str(e)}")
    
    # Demo information
    st.markdown("---")
    with st.expander("💡 Demo Information & Test Cards"):
        st.markdown("""
        **This is a demo payment system for testing purposes.**
        
        ### Test Card Numbers
        Use these cards for testing (all pass validation):
        
        **Visa:**
        - 4532015112830366
        - 4111111111111111
        
        **Mastercard:**
        - 5425233430109903
        - 5105105105105100
        
        **American Express:**
        - 378282246310005
        - 371449635398431
        
        ### Test Details
        - **CVV:** Any 3 digits (or 4 for Amex)
        - **Expiry:** Any future date (e.g., 12/25)
        - **Name:** Any name (e.g., John Doe)
        
        **Note:** All payments are mock and no real transactions occur.
        """)
        
        st.markdown("---")
        st.caption(f"Session ID: {session_id}")
        st.caption(f"Hold ID: {hold_id}")


# ==================== RUN APP ====================

if __name__ == "__main__":
    main()
