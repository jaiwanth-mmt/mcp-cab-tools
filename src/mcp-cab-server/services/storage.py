"""
Simple file-based storage for sharing data between MCP server and FastAPI backend.
This allows both processes to access the same booking holds and payment sessions.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any
import threading

# Storage file path
STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '.storage')
HOLDS_FILE = os.path.join(STORAGE_DIR, 'booking_holds.json')
PAYMENTS_FILE = os.path.join(STORAGE_DIR, 'payment_sessions.json')
PASSENGERS_FILE = os.path.join(STORAGE_DIR, 'passenger_data.json')

# Thread lock for file operations
_lock = threading.Lock()


def ensure_storage_dir():
    """Create storage directory if it doesn't exist"""
    os.makedirs(STORAGE_DIR, exist_ok=True)


def datetime_serializer(obj):
    """JSON serializer for datetime and date objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def datetime_deserializer(dct):
    """JSON deserializer for datetime strings"""
    for key, value in dct.items():
        if isinstance(value, str) and 'T' in value and ':' in value:
            try:
                dct[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
    return dct


def save_holds(holds: Dict[str, Any]):
    """Save booking holds to file"""
    ensure_storage_dir()
    with _lock:
        with open(HOLDS_FILE, 'w') as f:
            json.dump(holds, f, default=datetime_serializer, indent=2)


def load_holds() -> Dict[str, Any]:
    """Load booking holds from file"""
    ensure_storage_dir()
    if not os.path.exists(HOLDS_FILE):
        return {}
    
    with _lock:
        try:
            with open(HOLDS_FILE, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                for hold_id, hold in data.items():
                    if 'created_at' in hold and isinstance(hold['created_at'], str):
                        hold['created_at'] = datetime.fromisoformat(hold['created_at'])
                    if 'expires_at' in hold and isinstance(hold['expires_at'], str):
                        hold['expires_at'] = datetime.fromisoformat(hold['expires_at'])
                    if 'updated_at' in hold and isinstance(hold['updated_at'], str):
                        hold['updated_at'] = datetime.fromisoformat(hold['updated_at'])
                    if 'confirmed_at' in hold and isinstance(hold['confirmed_at'], str):
                        hold['confirmed_at'] = datetime.fromisoformat(hold['confirmed_at'])
                    if 'departure_date' in hold and isinstance(hold['departure_date'], str):
                        try:
                            hold['departure_date'] = datetime.fromisoformat(hold['departure_date']).date()
                        except:
                            pass
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {}


def save_payments(payments: Dict[str, Any]):
    """Save payment sessions to file"""
    ensure_storage_dir()
    with _lock:
        with open(PAYMENTS_FILE, 'w') as f:
            json.dump(payments, f, default=datetime_serializer, indent=2)


def load_payments() -> Dict[str, Any]:
    """Load payment sessions from file"""
    ensure_storage_dir()
    if not os.path.exists(PAYMENTS_FILE):
        return {}
    
    with _lock:
        try:
            with open(PAYMENTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                for session_id, session in data.items():
                    if 'created_at' in session and isinstance(session['created_at'], str):
                        session['created_at'] = datetime.fromisoformat(session['created_at'])
                    if 'expires_at' in session and isinstance(session['expires_at'], str):
                        session['expires_at'] = datetime.fromisoformat(session['expires_at'])
                    if 'completed_at' in session and isinstance(session['completed_at'], str):
                        session['completed_at'] = datetime.fromisoformat(session['completed_at'])
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {}


def save_passengers(passengers: Dict[str, Any]):
    """Save passenger data to file"""
    ensure_storage_dir()
    with _lock:
        with open(PASSENGERS_FILE, 'w') as f:
            json.dump(passengers, f, default=datetime_serializer, indent=2)


def load_passengers() -> Dict[str, Any]:
    """Load passenger data from file"""
    ensure_storage_dir()
    if not os.path.exists(PASSENGERS_FILE):
        return {}
    
    with _lock:
        try:
            with open(PASSENGERS_FILE, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects  
                for hold_id, passenger in data.items():
                    if 'added_at' in passenger and isinstance(passenger['added_at'], str):
                        passenger['added_at'] = datetime.fromisoformat(passenger['added_at'])
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {}


def clear_all_storage():
    """Clear all storage files (for testing)"""
    ensure_storage_dir()
    for file_path in [HOLDS_FILE, PAYMENTS_FILE, PASSENGERS_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
