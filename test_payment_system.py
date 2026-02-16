#!/usr/bin/env python3
"""
Quick test script to verify payment system installation
Run this to check if all components are properly set up
"""

import sys
import os

# Add src/mcp-cab-server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'mcp-cab-server'))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test models
        from models.models import (
            PaymentStatus, PaymentOrderRequest, PaymentOrderResponse,
            PaymentVerifyRequest, PaymentVerifyResponse,
            ConfirmBookingRequest, ConfirmBookingResponse,
            DriverDetails
        )
        print("  ✅ Payment models imported")
        
        # Test card validator
        from services.card_validator import (
            luhn_checksum, validate_card, get_card_type
        )
        print("  ✅ Card validator imported")
        
        # Test mock_db extensions
        from services.mock_db import (
            create_payment_session, get_payment_session,
            update_payment_status, assign_driver_to_booking,
            confirm_booking_final, MOCK_DRIVERS
        )
        print("  ✅ Mock DB payment functions imported")
        
        # Test payment service
        from services.payment import (
            create_payment_order_internal,
            get_payment_status_internal,
            confirm_booking_internal
        )
        print("  ✅ Payment service imported")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}\n")
        return False


def test_card_validation():
    """Test card validation functions"""
    print("🔍 Testing card validation...")
    
    from services.card_validator import validate_card, luhn_checksum, get_card_type
    from datetime import datetime
    
    # Calculate a future expiry date
    future_year = (datetime.now().year % 100) + 1  # Next year
    future_month = "12"
    future_expiry = f"{future_month}/{future_year}"
    
    # Test Luhn algorithm
    assert luhn_checksum("4532015112830366") == True, "Luhn validation failed"
    print("  ✅ Luhn algorithm working")
    
    # Test card type detection
    assert get_card_type("4532015112830366") == "visa", "Card type detection failed"
    assert get_card_type("5425233430109903") == "mastercard", "Card type detection failed"
    assert get_card_type("378282246310005") == "amex", "Card type detection failed"
    print("  ✅ Card type detection working")
    
    # Test full validation with future date
    valid, msg = validate_card("4532015112830366", "123", future_expiry, "John Doe")
    assert valid == True, f"Card validation failed: {msg}"
    print("  ✅ Full card validation working")
    
    # Test invalid card
    valid, msg = validate_card("1234567890123456", "123", future_expiry, "John Doe")
    assert valid == False, "Should reject invalid card"
    print("  ✅ Invalid card rejection working")
    
    print("\n✅ Card validation tests passed!\n")


def test_driver_pool():
    """Test driver pool"""
    print("🔍 Testing driver pool...")
    
    from services.mock_db import MOCK_DRIVERS
    
    assert len(MOCK_DRIVERS) > 0, "No drivers in pool"
    print(f"  ✅ Found {len(MOCK_DRIVERS)} drivers in pool")
    
    # Check driver structure
    driver = MOCK_DRIVERS[0]
    required_fields = ['name', 'phone', 'vehicle_number', 'vehicle_model', 'rating']
    for field in required_fields:
        assert field in driver, f"Driver missing field: {field}"
    print("  ✅ Driver structure validated")
    
    print("\n✅ Driver pool tests passed!\n")


def test_dependencies():
    """Test that required dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    try:
        import fastapi
        print(f"  ✅ FastAPI {fastapi.__version__} installed")
    except ImportError:
        print("  ❌ FastAPI not installed")
        return False
    
    try:
        import uvicorn
        print(f"  ✅ Uvicorn {uvicorn.__version__} installed")
    except ImportError:
        print("  ❌ Uvicorn not installed")
        return False
    
    try:
        import streamlit
        print(f"  ✅ Streamlit {streamlit.__version__} installed")
    except ImportError:
        print("  ❌ Streamlit not installed")
        return False
    
    try:
        import httpx
        print(f"  ✅ HTTPX {httpx.__version__} installed")
    except ImportError:
        print("  ❌ HTTPX not installed")
        return False
    
    print("\n✅ All dependencies installed!\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Payment System Installation Test")
    print("=" * 60)
    print()
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed. Please check your installation.")
        sys.exit(1)
    
    # Test card validation
    try:
        test_card_validation()
    except Exception as e:
        print(f"❌ Card validation tests failed: {e}")
        sys.exit(1)
    
    # Test driver pool
    try:
        test_driver_pool()
    except Exception as e:
        print(f"❌ Driver pool tests failed: {e}")
        sys.exit(1)
    
    # Test dependencies
    if not test_dependencies():
        print("❌ Dependency tests failed. Run 'uv sync' to install.")
        sys.exit(1)
    
    # Success!
    print("=" * 60)
    print("🎉 All tests passed! Payment system is ready to use.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Terminal 1: python src/mcp-cab-server/server.py")
    print("2. Terminal 2: uv run uvicorn src.mcp-cab-server.payment_backend:app --reload --port 8000")
    print("3. Terminal 3: uv run streamlit run src/mcp-cab-server/payment_frontend.py --server.port 8501")
    print()
    print("See PAYMENT_GUIDE.md for detailed usage instructions.")
    print()


if __name__ == "__main__":
    main()
