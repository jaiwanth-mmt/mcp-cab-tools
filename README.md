# MCP Cab Search & Book Server

A complete Model Context Protocol (MCP) server for searching, booking, and managing cab rides with real-time location autocomplete, secure payment processing, and booking management.

## Features

### 🔍 Location Services
- **Real-time Location Search**: Powered by Google Places Autocomplete API
- **Smart Location Resolution**: Automatic geocoding with precise coordinates
- **Interactive Disambiguation**: Dropdown selection when multiple locations match
- **Fuzzy Matching**: Intelligent fallback for route matching

### 🚕 Booking Management
- **Cab Search**: Find available cabs between any two locations
- **Hold System**: 15-minute temporary booking holds
- **Passenger Details**: Capture passenger information securely
- **Trip Planning**: Support for one-way, round-trip, hourly rental, and airport transfers

### 💳 Payment System
- **Mock Payment Gateway**: Realistic payment simulation with Streamlit frontend
- **Card Validation**: Luhn algorithm validation, expiry checks, CVV validation
- **Payment Sessions**: Secure session management with expiration
- **Test Cards**: Multiple test cards for Visa, Mastercard, Amex, and Discover

### 📋 Complete Booking Flow
- **Driver Assignment**: Automatic assignment from driver pool
- **Booking Confirmation**: Final confirmation with complete trip details
- **Status Tracking**: Real-time booking status updates
- **Cross-process Data Sharing**: File-based storage for multi-process architecture

## Architecture

### Google Places API Integration

The server uses two Google Places API endpoints:

1. **Places Autocomplete API**: Returns location suggestions as user types
   - Endpoint: `https://maps.googleapis.com/maps/api/place/autocomplete/json`
   - Returns: List of place suggestions with `place_id`, `name`, and `formatted_address`

2. **Places Details API**: Fetches complete location details including coordinates
   - Endpoint: `https://maps.googleapis.com/maps/api/place/details/json`
   - Returns: Full place information with exact latitude/longitude

### Complete Booking Flow

```
1. Search Phase
   User Input → Autocomplete API → Location Disambiguation
        ↓
   Search Cabs → Return Available Options

2. Booking Phase
   Select Cab → Create Hold (15 min expiry)
        ↓
   Add Passenger Details → Generate Payment Link

3. Payment Phase
   Open Payment URL → Enter Card Details → Validate
        ↓
   Process Payment → Update Session Status

4. Confirmation Phase
   Verify Payment → Assign Driver → Confirm Booking
        ↓
   Return Booking Details with Driver Info
```

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP)                 │
│  - Location Services (Google Places API)               │
│  - Booking Management (Hold, Passenger, Status)        │
│  - Payment Tools (Create Order, Verify, Confirm)       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              File-based Storage (.storage/)             │
│  - booking_holds.json                                   │
│  - payment_sessions.json                                │
│  - passenger_data.json                                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────┬─────────────────────────┬─────────────────┐
│  FastAPI    │   Streamlit Frontend    │  Mock Services  │
│  Backend    │   (Payment UI)          │  (DB, Drivers)  │
│  Port: 8000 │   Port: 8501            │                 │
└─────────────┴─────────────────────────┴─────────────────┘
```

## Setup

### Prerequisites

- Python 3.11+
- Google Cloud Project with Places API enabled
- Google Places API Key (required for location services)

### Installation

1. Clone the repository:
```bash
cd mcp-cabs-search-book
```

2. Install dependencies using `uv`:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

3. Configure Environment:

Create a `.env` file in the project root:
```env
GOOGLE_PLACES_API_KEY=your_actual_api_key_here
```

**Important Security Notes:**
- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Never share your API keys publicly
- Restrict your API key to only required services in Google Cloud Console

### Getting a Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API (New)
   - Or: Places API, Geocoding API (if using legacy)
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the API key to your `.env` file
6. (Optional) Restrict the API key to only Places API for security

### Running the Complete System

The system requires three separate processes for full functionality:

#### 1. Start MCP Server (Terminal 1)
```bash
python main.py
# or
python src/mcp-cab-server/server.py
```

#### 2. Start Payment Backend (Terminal 2)
```bash
uv run uvicorn src.mcp-cab-server.payment_backend:app --reload --port 8000
```

#### 3. Start Payment Frontend (Terminal 3)
```bash
uv run streamlit run src/mcp-cab-server/payment_frontend.py --server.port 8501
```

**Note:** For basic cab search functionality, only the MCP Server (step 1) is required. The payment components (steps 2-3) are needed for the complete booking flow.

## Usage

### Complete Booking Flow Example

#### Step 1: Search for Cabs
```python
Search_cabs(
    pickup="Delhi Airport",
    drop="Connaught Place",
    trip_type="one way",
    departure_date="2024-02-20"
)
```

#### Step 2: Create Booking Hold
```python
hold_cab_booking(
    cab_id="DEL_IGI_CP_2",
    pickup="Indira Gandhi International Airport",
    drop="Connaught Place",
    departure_date="2024-02-20"
)
# Returns: hold_id (valid for 15 minutes)
```

#### Step 3: Add Passenger Details
```python
add_passenger_details(
    hold_id="HOLD_1001",
    passenger_name="John Doe",
    passenger_phone="+919876543210",
    passenger_email="john@example.com"
)
```

#### Step 4: Create Payment Order
```python
create_payment_order(hold_id="HOLD_1001")
# Returns: payment_url (opens in browser)
```

#### Step 5: Complete Payment
- Open the payment URL in your browser
- Enter card details (use test cards provided)
- Submit payment

#### Step 6: Verify Payment
```python
verify_mock_payment(session_id="PAY_5001")
# Returns: payment status
```

#### Step 7: Confirm Booking
```python
confirm_booking(hold_id="HOLD_1001")
# Returns: booking_id, driver details, confirmation
```

### Test Cards

Use these cards in the payment frontend:

| Card Type | Number | CVV | Expiry |
|-----------|--------|-----|--------|
| Visa | 4532015112830366 | 123 | Any future date |
| Visa | 4111111111111111 | 123 | Any future date |
| Mastercard | 5425233430109903 | 123 | Any future date |
| Amex | 378282246310005 | 1234 | Any future date |
| Discover | 6011111111111117 | 123 | Any future date |

**Note:** All payments are mock transactions. No real money is processed.

### Testing the System

#### Quick Payment System Test
```bash
python test_payment_system.py
```

This verifies:
- All imports and dependencies
- Card validation (Luhn algorithm)
- Driver pool availability
- Module integrity

## Project Structure

```
mcp-cabs-search-book/
├── .env                              # Environment variables (not in repo)
├── .gitignore                        # Git ignore patterns
├── pyproject.toml                    # Project dependencies
├── README.md                         # This file
├── main.py                           # MCP server entry point
├── test_payment_system.py            # Payment system tests
└── src/
    ├── .storage/                     # File-based data storage (gitignored)
    │   ├── booking_holds.json        # Active booking holds
    │   ├── payment_sessions.json     # Payment session data
    │   └── passenger_data.json       # Passenger information
    └── mcp-cab-server/
        ├── server.py                 # Main MCP server with tools
        ├── payment_backend.py        # FastAPI payment backend
        ├── payment_frontend.py       # Streamlit payment UI
        ├── models/
        │   └── models.py             # All Pydantic models
        └── services/
            ├── geocoding.py          # Google Places API integration
            ├── helper.py             # Cab search & booking logic
            ├── mock_db.py            # Mock database with routes
            ├── payment.py            # Payment service layer
            ├── card_validator.py     # Card validation (Luhn, etc.)
            └── storage.py            # File-based storage utilities
```

## API Reference

### MCP Tools

#### 1. `Search_cabs`
Search for available cabs between two locations.

**Input:**
```python
{
  "pickup": str,              # Pickup location
  "drop": str,                # Drop location  
  "trip_type": TripType,      # Trip type
  "departure_date": date      # Journey date
}
```

**Output:**
```python
{
  "cabs": [
    {"cab_id": str, "cab_type": str, "price": int}
  ]
}
```

#### 2. `hold_cab_booking`
Create a 15-minute temporary hold on a cab.

**Input:**
```python
{
  "cab_id": str,              # From search results
  "pickup": str,              # Pickup location
  "drop": str,                # Drop location
  "departure_date": date      # Journey date
}
```

**Output:**
```python
{
  "hold_id": str,             # Unique hold identifier
  "expires_at": str,          # ISO timestamp
  "cab_details": dict,        # Cab information
  "price": int                # Total price
}
```

#### 3. `add_passenger_details`
Add passenger information to a booking hold.

**Input:**
```python
{
  "hold_id": str,             # From hold_cab_booking
  "passenger_name": str,      # Full name
  "passenger_phone": str,     # Contact number
  "passenger_email": str,     # Email (optional)
  "special_requests": str     # Special requirements (optional)
}
```

#### 4. `create_payment_order`
Generate a payment link for the booking.

**Input:**
```python
{
  "hold_id": str              # Hold with passenger details
}
```

**Output:**
```python
{
  "session_id": str,          # Payment session ID
  "payment_url": str,         # URL to open in browser
  "amount": float,            # Payment amount
  "expires_at": str           # Session expiry
}
```

#### 5. `verify_mock_payment`
Check payment completion status.

**Input:**
```python
{
  "session_id": str           # From create_payment_order
}
```

**Output:**
```python
{
  "status": str,              # "pending", "completed", "failed"
  "amount": float,
  "card_last4": str           # Last 4 digits (if completed)
}
```

#### 6. `confirm_booking`
Finalize booking after payment, assign driver.

**Input:**
```python
{
  "hold_id": str              # Hold with completed payment
}
```

**Output:**
```python
{
  "booking_id": str,          # Final booking reference
  "driver": {
    "name": str,
    "phone": str,
    "vehicle_number": str,
    "vehicle_model": str,
    "rating": float
  },
  "booking_summary": dict     # Complete trip details
}
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_PLACES_API_KEY` | Yes | Google Places API key for location services |

### Data Storage

The system uses file-based JSON storage in `src/.storage/`:
- **booking_holds.json**: Active booking holds and their status
- **payment_sessions.json**: Payment session tracking
- **passenger_data.json**: Passenger information per hold

**Note:** The `.storage/` directory is gitignored and created automatically at runtime.

### API Costs (Approximate)

- **Places Autocomplete**: ~$2.83 per 1,000 requests
- **Place Details**: ~$17 per 1,000 requests
- **Total per cab search**: ~$0.04 (2 autocomplete + 2 details calls)

### System Ports

| Service | Port | Purpose |
|---------|------|---------|
| MCP Server | stdio | Main MCP protocol server |
| Payment Backend | 8000 | FastAPI REST API |
| Payment Frontend | 8501 | Streamlit payment UI |

## Development

### Adding Mock Routes

Edit `src/mcp-cab-server/services/mock_db.py`:

```python
MOCK_CAB_DB = {
    ("pickup_location_name", "drop_location_name"): [
        {"cab_id": "ROUTE_ID", "cab_type": "sedan", "price": 500},
        {"cab_id": "ROUTE_ID_2", "cab_type": "suv", "price": 700},
    ],
}
```

**Note:** Location names should match Google Places API output (lowercase).

### Adding Mock Drivers

Edit the `MOCK_DRIVERS` list in `mock_db.py`:

```python
MOCK_DRIVERS = [
    {
        "name": "Driver Name",
        "phone": "+91-9876543210",
        "vehicle_number": "DL-01-AB-1234",
        "vehicle_model": "Honda City",
        "rating": 4.8
    }
]
```

### Extending the Server

1. **Add MCP Tools**: Decorate functions with `@mcp.tool()` in `server.py`
2. **Add Models**: Define Pydantic models in `models/models.py`
3. **Add Services**: Create service modules in `services/`
4. **Add API Endpoints**: Add FastAPI routes in `payment_backend.py`

### Code Structure

- **Clean Code**: Comments removed for clarity, only essential inline comments remain
- **Type Safety**: Full Pydantic model validation throughout
- **Error Handling**: Comprehensive error messages with logging
- **Storage**: Thread-safe file-based storage with automatic serialization

## Troubleshooting

### Location Services

#### "GOOGLE_PLACES_API_KEY not found"
- Ensure `.env` file exists in project root
- Verify format: `GOOGLE_PLACES_API_KEY=your_key` (no quotes)
- Check API key is valid in Google Cloud Console
- Verify Places API is enabled and billing is active

#### "No locations found"
- Check API key permissions and quotas
- Verify billing is enabled on Google Cloud project
- Try less specific search terms
- Check server logs for detailed errors

### Payment System

#### Payment frontend won't start
- Ensure all dependencies installed: `uv sync`
- Check port 8501 is available
- Verify payment backend is running on port 8000

#### Card validation fails
- Use provided test cards (see Test Cards section)
- Ensure expiry date is in future (MM/YY format)
- CVV: 3 digits (4 for Amex)
- Check browser console for detailed errors

#### "Hold has expired"
- Holds expire after 15 minutes
- Create a new cab hold and retry quickly
- Check system time is synchronized

### Storage Issues

#### "Permission denied" on .storage files
- Ensure write permissions on project directory
- Check `.storage/` directory is not read-only
- Verify no other process is locking the files

### General Issues

#### Import warnings in IDE
- Normal for this project structure
- Code works correctly at runtime
- PYTHONPATH is set properly by the entry points

#### Multiple processes coordination
- Start MCP server first
- Then start payment backend
- Finally start payment frontend
- All three must run simultaneously for full functionality

## Security Notes

### What's Safe
- ✅ All payments are mock/simulated
- ✅ No real financial transactions occur
- ✅ Test card numbers are public domain
- ✅ No sensitive data stored permanently
- ✅ `.env` file is gitignored

### Important Reminders
- 🔒 Never commit `.env` file to version control
- 🔒 Never share your Google API key publicly
- 🔒 Use API key restrictions in Google Cloud Console
- 🔒 Keep `.storage/` directory gitignored
- 🔒 This is a demonstration system only

## Testing & Validation

### Card Validation Features
- **Luhn Algorithm**: Validates card checksum
- **Card Type Detection**: Identifies Visa, Mastercard, Amex, Discover
- **Expiry Validation**: Checks for expired cards
- **CVV Length**: Validates based on card type (3 or 4 digits)
- **Cardholder Name**: Basic format validation

### Booking Hold System
- **15-Minute Expiry**: Automatic hold expiration
- **Status Tracking**: held → passenger_added → payment_pending → payment_success → confirmed
- **Cleanup Thread**: Background cleanup of old expired holds
- **Thread-Safe Storage**: Concurrent access protection

## Production Considerations

**⚠️ This is a demonstration project. For production use:**

1. Replace mock payment with real gateway (Stripe, Razorpay, etc.)
2. Use proper database (PostgreSQL, MongoDB)
3. Add authentication and authorization
4. Implement rate limiting and API security
5. Add comprehensive logging and monitoring
6. Use environment-specific configurations
7. Add unit and integration tests
8. Implement proper error handling and retry logic
9. Add data encryption for sensitive information
10. Use message queues for background tasks

## License

This project is for demonstration and educational purposes.

## Contributing

Feel free to fork and extend this demonstration project!

## Support

For issues:
1. Check server logs for detailed error messages
2. Run `python test_payment_system.py` to verify setup
3. Verify Google API key and billing status
4. Ensure all three processes are running
5. Check browser console for frontend errors
