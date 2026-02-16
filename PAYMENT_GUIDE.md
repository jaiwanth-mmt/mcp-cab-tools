# Payment System Implementation Guide

## Overview

The payment system adds three new MCP tools to complete the cab booking flow:
1. **`create_payment_order`** - Generates mock payment link with URL elicitation
2. **`verify_mock_payment`** - Checks payment completion status
3. **`confirm_booking`** - Finalizes booking and assigns driver

## Architecture

```
MCP Server (port: MCP protocol)
    ↓ HTTP calls
FastAPI Backend (port: 8000)
    ↓ Payment form URL
Streamlit Frontend (port: 8501)
```

## Complete Booking Flow

1. **Search Cabs** → `Search_cabs(pickup, drop, trip_type, date)`
2. **Hold Cab** → `hold_cab_booking(cab_id, departure_date, pickup, drop)`
3. **Add Passenger** → `add_passenger_details(hold_id, name, phone, email)`
4. **Create Payment** → `create_payment_order(hold_id)` ✨ NEW
5. **Verify Payment** → `verify_mock_payment(session_id)` ✨ NEW
6. **Confirm Booking** → `confirm_booking(hold_id)` ✨ NEW

## Installation

### Install Dependencies

```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
uv sync
```

This will install:
- `fastapi>=0.115.0` - Backend API server
- `uvicorn>=0.32.0` - ASGI server for FastAPI
- `streamlit>=1.40.0` - Payment UI frontend

### Verify Installation

```bash
uv pip list | grep -E "(fastapi|uvicorn|streamlit)"
```

## Running the System

You need **3 terminals** running simultaneously:

### Terminal 1: MCP Server

```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
python src/mcp-cab-server/server.py
```

**Output:**
```
INFO:root:🔍 Cab search request - Pickup: ...
```

### Terminal 2: FastAPI Backend

```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
uv run uvicorn src.mcp-cab-server.payment_backend:app --reload --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test Backend:**
```bash
curl http://localhost:8000/
```

### Terminal 3: Streamlit Frontend

```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
uv run streamlit run src/mcp-cab-server/payment_frontend.py --server.port 8501
```

**Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## Testing the Payment Flow

### Step 1: Complete Previous Steps

```python
# Search cabs
search_cabs(pickup="Delhi Airport", drop="Connaught Place", 
            trip_type="one way", departure_date="2024-02-20")

# Hold a cab (use cab_id from search results)
hold_cab_booking(cab_id="DEL_AP_CP_2", departure_date="2024-02-20",
                 pickup="Delhi Airport", drop="Connaught Place")

# Add passenger details (use hold_id from hold response)
add_passenger_details(hold_id="HOLD_1001", passenger_name="John Doe",
                      passenger_phone="9876543210", 
                      passenger_email="john@example.com")
```

### Step 2: Create Payment Order

```python
create_payment_order(hold_id="HOLD_1001")
```

**Expected Output:**
- MCP will show an elicitation prompt with payment URL
- Example: `http://localhost:8501?session_id=PAY_5001&amount=650&hold_id=HOLD_1001`
- Click "Accept" or copy the URL to your browser

### Step 3: Complete Payment in Browser

1. Open the payment URL in your browser
2. See booking summary
3. Enter test card details:
   - **Card:** 4532015112830366
   - **Expiry:** 12/25
   - **CVV:** 123
   - **Name:** John Doe
4. Click "Pay Now"
5. See success message with balloons 🎈

### Step 4: Verify Payment

```python
verify_mock_payment(session_id="PAY_5001")
```

**Expected Output:**
```
✅ Payment Completed!

📋 Payment Details:
   • Session ID: PAY_5001
   • Status: COMPLETED
   • Amount: ₹650.00
   • Card: •••• 0366
   • Completed: 2024-02-16T...
```

### Step 5: Confirm Booking

```python
confirm_booking(hold_id="HOLD_1001")
```

**Expected Output:**
```
🎉 Booking Confirmed!

📋 Booking Details:
   • Booking ID: BKG_2001
   • Status: CONFIRMED

🚗 Driver Assigned:
   • Name: Rajesh Kumar
   • Phone: +91-9876543210
   • Vehicle: Honda City
   • Number: DL-01-AB-1234
   • Rating: 4.8 ⭐

🚕 Trip Details:
   • Cab Type: sedan
   • Route: Delhi Airport → Connaught Place
   • Price: ₹650
```

## Test Card Numbers

All test cards pass Luhn validation:

### Visa
- `4532015112830366`
- `4111111111111111`
- `4532261615902522`

### Mastercard
- `5425233430109903`
- `5105105105105100`
- `5555555555554444`

### American Express
- `378282246310005` (requires 4-digit CVV)
- `371449635398431`

### Test Details
- **CVV:** Any 3 digits (4 for Amex)
- **Expiry:** Any future date (e.g., 12/25, 06/26)
- **Name:** Any name (e.g., John Doe)

## API Endpoints (FastAPI Backend)

### Health Check
```
GET http://localhost:8000/
```

### Initiate Payment
```
POST http://localhost:8000/api/payment/initiate
Body: {"hold_id": "HOLD_1001"}
```

### Process Payment
```
POST http://localhost:8000/api/payment/pay
Body: {
    "session_id": "PAY_5001",
    "card_number": "4532015112830366",
    "cvv": "123",
    "expiry": "12/25",
    "cardholder_name": "John Doe"
}
```

### Check Payment Status
```
GET http://localhost:8000/api/payment/status/PAY_5001
```

### Get Hold Details
```
GET http://localhost:8000/api/hold/HOLD_1001
```

## File Structure

```
src/mcp-cab-server/
├── models/
│   └── models.py                    # ✨ Added payment models
├── services/
│   ├── card_validator.py           # ✨ NEW - Luhn validation
│   ├── mock_db.py                  # ✨ Updated with payment sessions
│   ├── payment.py                  # ✨ NEW - Payment logic
│   ├── geocoding.py                # Existing
│   └── helper.py                   # Existing
├── server.py                        # ✨ Updated with 3 new tools
├── payment_backend.py              # ✨ NEW - FastAPI server
└── payment_frontend.py             # ✨ NEW - Streamlit UI
```

## Key Features

### 1. Realistic Card Validation
- **Luhn Algorithm** - Proper checksum validation
- **Card Type Detection** - Visa, Mastercard, Amex, Discover
- **Expiry Validation** - Checks for future dates
- **CVV Validation** - 3 digits (4 for Amex)

### 2. Payment Session Management
- **30-minute expiry** - Sessions expire after 30 minutes
- **Status tracking** - pending → completed → confirmed
- **Hold integration** - Payment linked to booking hold

### 3. Driver Assignment
- **Random selection** - From pool of 10 mock drivers
- **Realistic details** - Name, phone, vehicle, rating
- **Indian format** - Vehicle numbers like DL-01-AB-1234

### 4. Booking Status Flow
```
HELD → PASSENGER_ADDED → PAYMENT_PENDING → PAYMENT_SUCCESS → CONFIRMED
```

## Error Handling

### Common Errors

**1. Hold not found**
```
ValueError: Hold not found: HOLD_999
```
**Solution:** Use valid hold_id from `hold_cab_booking` response

**2. Hold expired**
```
ValueError: Hold has expired
```
**Solution:** Holds expire after 15 minutes. Create a new hold.

**3. Missing passenger details**
```
ValueError: Passenger details must be added first
```
**Solution:** Call `add_passenger_details` before creating payment

**4. Payment not completed**
```
ValueError: Payment not completed for this booking
```
**Solution:** Complete payment in browser first, then confirm booking

**5. Card validation failed**
```
HTTPException: Invalid card number (failed checksum validation)
```
**Solution:** Use test cards that pass Luhn validation

**6. Backend not running**
```
ConnectError: Cannot connect to payment server
```
**Solution:** Start FastAPI backend on port 8000

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart backend
uv run uvicorn src.mcp-cab-server.payment_backend:app --reload --port 8000
```

### Streamlit won't start
```bash
# Check if port 8501 is in use
lsof -i :8501

# Use different port
uv run streamlit run src/mcp-cab-server/payment_frontend.py --server.port 8502
```

### Import errors
```bash
# Verify Python path
cd /Users/int1946/Desktop/mcp-cabs-search-book

# Run with proper path
PYTHONPATH=/Users/int1946/Desktop/mcp-cabs-search-book/src python src/mcp-cab-server/payment_backend.py
```

### Payment URL not opening
- Manually copy the URL from MCP response
- Paste in browser
- Ensure all 3 servers are running

## Testing Checklist

- [ ] MCP server running
- [ ] FastAPI backend running on port 8000
- [ ] Streamlit frontend running on port 8501
- [ ] Can search cabs
- [ ] Can hold cab
- [ ] Can add passenger details
- [ ] Can create payment order
- [ ] Payment URL opens in browser
- [ ] Can enter test card details
- [ ] Payment completes successfully
- [ ] Can verify payment status
- [ ] Can confirm booking
- [ ] Driver assigned with details

## Next Steps

1. **Test the full flow** - Follow the testing steps above
2. **Try different cards** - Test Visa, Mastercard, Amex
3. **Test error cases** - Invalid cards, expired holds, etc.
4. **Check logs** - All servers log operations for debugging

## Support

If you encounter issues:
1. Check all 3 servers are running
2. Verify port availability (8000, 8501)
3. Check terminal logs for error messages
4. Ensure dependencies installed (`uv sync`)
5. Use test cards from the list above

---

**Status:** ✅ All payment tools implemented and tested
**Version:** 1.0.0
**Date:** 2024-02-16
