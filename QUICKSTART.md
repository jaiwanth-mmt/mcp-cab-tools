# 🚀 Quick Start Guide - Payment System

## One-Time Setup

```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book

# Install dependencies
uv sync

# Test installation
python test_payment_system.py
```

## Running the System (3 Terminals)

### Terminal 1: MCP Server ⚙️
```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
python src/mcp-cab-server/server.py
```

### Terminal 2: Backend API 🔧
```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
uv run uvicorn src.mcp-cab-server.payment_backend:app --reload --port 8000
```
**Note:** If you see import errors, restart the terminal or press Ctrl+C and run again.

### Terminal 3: Payment UI 💳
```bash
cd /Users/int1946/Desktop/mcp-cabs-search-book
uv run streamlit run src/mcp-cab-server/payment_frontend.py --server.port 8501
```

## Testing Flow

### 1️⃣ Search & Hold
```python
# In MCP chat
search_cabs(pickup="Delhi Airport", drop="Connaught Place", 
            trip_type="one way", departure_date="2024-02-20")

hold_cab_booking(cab_id="DEL_AP_CP_2", departure_date="2024-02-20",
                 pickup="Delhi Airport", drop="Connaught Place")
```

### 2️⃣ Add Passenger
```python
add_passenger_details(
    hold_id="HOLD_1001",
    passenger_name="John Doe",
    passenger_phone="9876543210",
    passenger_email="john@example.com"
)
```

### 3️⃣ Create Payment
```python
create_payment_order(hold_id="HOLD_1001")
# Click accept, open URL in browser
```

### 4️⃣ Pay in Browser
- Card: `4532015112830366`
- Expiry: `12/25`
- CVV: `123`
- Name: `John Doe`

### 5️⃣ Verify Payment
```python
verify_mock_payment(session_id="PAY_5001")
```

### 6️⃣ Confirm Booking
```python
confirm_booking(hold_id="HOLD_1001")
# Driver assigned! 🎉
```

## Test Cards 💳

| Type | Number | CVV |
|------|--------|-----|
| Visa | 4532015112830366 | 123 |
| Visa | 4111111111111111 | 123 |
| Mastercard | 5425233430109903 | 123 |
| Amex | 378282246310005 | 1234 |

## Common Issues 🔧

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :8501

# Kill the process
kill -9 <PID>
```

### Backend Won't Connect
- Check Terminal 2 is running
- Visit http://localhost:8000 in browser
- Should see: `{"status":"ok"}`

### Payment URL Won't Open
- Copy URL manually from MCP response
- Paste in browser
- Ensure Terminal 3 is running

## Full Documentation 📚

- **PAYMENT_GUIDE.md** - Complete usage guide
- **IMPLEMENTATION_SUMMARY.md** - What was built
- **test_payment_system.py** - Test script

## Booking Status Flow

```
HELD → PASSENGER_ADDED → PAYMENT_PENDING → PAYMENT_SUCCESS → CONFIRMED
```

## Need Help? 🆘

1. Check all 3 terminals are running
2. Run test script: `python test_payment_system.py`
3. Check logs in terminals for errors
4. Verify ports 8000 and 8501 are free

---

**Quick tip:** Keep all 3 terminals visible side-by-side to monitor logs! 👀
