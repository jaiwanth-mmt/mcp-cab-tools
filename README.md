# MCP Cab Search & Book Server

A Model Context Protocol (MCP) server for searching and booking cabs with real-time location autocomplete using Google Places API.

## Features

- 🔍 **Real-time Location Search**: Powered by Google Places Autocomplete API
- 🗺️ **Smart Location Resolution**: Automatic geocoding with precise coordinates
- 🚕 **Cab Availability**: Search available cabs between pickup and drop locations
- 💬 **Interactive Elicitation**: When multiple locations match, users can select from a dropdown
- 📅 **Trip Planning**: Support for different trip types (one-way, round-trip, hourly rental, airport transfer)

## Architecture

### Google Places API Integration

The server uses two Google Places API endpoints:

1. **Places Autocomplete API**: Returns location suggestions as user types
   - Endpoint: `https://maps.googleapis.com/maps/api/place/autocomplete/json`
   - Returns: List of place suggestions with `place_id`, `name`, and `formatted_address`

2. **Places Details API**: Fetches complete location details including coordinates
   - Endpoint: `https://maps.googleapis.com/maps/api/place/details/json`
   - Returns: Full place information with exact latitude/longitude

### Flow Diagram

```
User Input → Autocomplete API → Multiple Suggestions?
                                      ├─ Yes → Elicitation (User Selects)
                                      └─ No  → Auto-select
                                           ↓
                                   Details API → Coordinates
                                           ↓
                                   Search Available Cabs
                                           ↓
                                   Return Results
```

## Setup

### Prerequisites

- Python 3.11+
- Google Cloud Project with Places API enabled
- Google Places API Key

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

3. Configure Google API Key:

Create a `.env` file in the project root:
```env
GOOGLE_PLACES_API_KEY=your_actual_api_key_here
```

**Important**: Never commit your `.env` file to version control!

### Getting a Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API (New)
   - Or: Places API, Geocoding API (if using legacy)
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the API key to your `.env` file
6. (Optional) Restrict the API key to only Places API for security

### Running the Server

Start the MCP server:

```bash
python src/mcp-cab-server/server.py
```

Or using the main entry point:

```bash
python main.py
```

## Usage

### Using with MCP Inspector

1. Install MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2. Connect to the server and test the `Search_cabs` tool

3. Example input:
```json
{
  "pickup": "Mumbai Airport",
  "drop": "Gateway of India",
  "trip_type": "one way",
  "departure_date": "2024-02-15"
}
```

4. If multiple locations match, you'll see an elicitation prompt:
```
🚕 Found 3 locations for 'Mumbai Airport'. Please select the pickup location:
1. Chhatrapati Shivaji Maharaj International Airport - Mumbai, Maharashtra
2. Mumbai Domestic Airport - Andheri, Mumbai
3. Mumbai Airport Metro Station - Mumbai
```

5. Select the desired location and the server will fetch available cabs

### Testing the Integration

Run the test script to verify Google API integration:

```bash
python test_integration.py
```

This will:
- Test location autocomplete with various queries
- Verify location resolution with coordinates
- Simulate the elicitation flow
- Display results in the terminal

## Project Structure

```
mcp-cabs-search-book/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore file
├── pyproject.toml                # Project dependencies
├── README.md                     # This file
├── test_integration.py           # Integration tests
├── main.py                       # Entry point
└── src/
    └── mcp-cab-server/
        ├── server.py             # FastMCP server definition
        ├── models/
        │   ├── __init__.py
        │   └── models.py         # Pydantic models
        └── services/
            ├── __init__.py
            ├── geocoding.py      # Google Places API integration
            ├── helper.py         # Cab search logic
            └── mock_db.py        # Mock cab database
```

## API Reference

### Tool: `Search_cabs`

Search for available cabs between two locations.

**Input Schema:**
```python
{
  "pickup": str,              # Pickup location (e.g., "Mumbai Airport")
  "drop": str,                # Drop location (e.g., "Gateway of India")
  "trip_type": TripType,      # "one way" | "round trip" | "Hourly rental" | "Airport Transfer"
  "departure_date": date      # Format: "DD-MM-YYYY" or "YYYY-MM-DD"
}
```

**Output Schema:**
```python
{
  "cabs": [
    {
      "cab_type": str,        # e.g., "sedan", "suv", "mini"
      "price": int            # Price in local currency
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_PLACES_API_KEY` | Yes | Your Google Places API key |

### API Costs (Approximate)

- **Places Autocomplete**: ~$2.83 per 1,000 requests
- **Place Details**: ~$17 per 1,000 requests
- **Total per search**: ~$0.04 (2 autocomplete + 2 details calls)

## Development

### Adding New Mock Cab Routes

Edit `src/mcp-cab-server/services/mock_db.py`:

```python
MOCK_CAB_DB = {
    ("pickup_location_name", "drop_location_name"): [
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
}
```

**Note**: The location names must match the `name` field returned by Google Places API (lowercase).

### Extending the Server

1. **Add new tools**: Create new functions in `server.py` decorated with `@mcp.tool()`
2. **Add models**: Define Pydantic models in `models/models.py`
3. **Add services**: Create service modules in `services/`

## Troubleshooting

### "GOOGLE_PLACES_API_KEY not found"

Make sure:
1. `.env` file exists in the project root
2. The file contains: `GOOGLE_PLACES_API_KEY=your_key`
3. The key has no quotes around it
4. You've run `load_dotenv()` before using the API

### "No results found"

Check:
1. API key is valid and has Places API enabled
2. You have billing enabled on your Google Cloud project
3. The query is not too specific or misspelled
4. Check logs for detailed error messages

### Import errors in IDE

The import warnings are normal for this project structure. The code will work at runtime because the PYTHONPATH is set correctly when running the server.

## License

This project is for demonstration purposes.

## Contributing

This is a demonstration project. Feel free to fork and extend!

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify your Google API key is valid
3. Test with the `test_integration.py` script
4. Review the Google Places API documentation
