"""
Card Validation Utilities
Provides realistic card validation including Luhn algorithm, card type detection,
and comprehensive validation for mock payment processing.
"""

from datetime import datetime
from typing import Tuple


def luhn_checksum(card_number: str) -> bool:
    """
    Validate card number using Luhn algorithm (mod 10 algorithm).
    
    Args:
        card_number: Card number string (digits only)
    
    Returns:
        True if valid, False otherwise
    """
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10 == 0


def get_card_type(card_number: str) -> str:
    """
    Detect card type based on card number prefix.
    
    Args:
        card_number: Card number string (digits only)
    
    Returns:
        Card type: 'visa', 'mastercard', 'amex', 'discover', or 'unknown'
    """
    # Remove spaces and dashes
    card_clean = card_number.replace(" ", "").replace("-", "")
    
    if not card_clean.isdigit():
        return "unknown"
    
    # Visa: starts with 4
    if card_clean.startswith("4"):
        return "visa"
    
    # Mastercard: starts with 51-55 or 2221-2720
    if card_clean[:2] in ["51", "52", "53", "54", "55"]:
        return "mastercard"
    if len(card_clean) >= 4:
        prefix = int(card_clean[:4])
        if 2221 <= prefix <= 2720:
            return "mastercard"
    
    # American Express: starts with 34 or 37
    if card_clean[:2] in ["34", "37"]:
        return "amex"
    
    # Discover: starts with 6011, 622126-622925, 644-649, or 65
    if card_clean.startswith("6011") or card_clean.startswith("65"):
        return "discover"
    if len(card_clean) >= 6:
        prefix = int(card_clean[:6])
        if 622126 <= prefix <= 622925:
            return "discover"
    if len(card_clean) >= 3:
        prefix = int(card_clean[:3])
        if 644 <= prefix <= 649:
            return "discover"
    
    return "unknown"


def validate_expiry(expiry_str: str) -> Tuple[bool, str]:
    """
    Validate card expiry date.
    
    Args:
        expiry_str: Expiry date in MM/YY format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if "/" not in expiry_str:
        return False, "Expiry must be in MM/YY format"
    
    parts = expiry_str.split("/")
    if len(parts) != 2:
        return False, "Expiry must be in MM/YY format"
    
    month_str, year_str = parts
    
    # Validate format
    if len(month_str) != 2 or len(year_str) != 2:
        return False, "Expiry must be in MM/YY format (e.g., 12/25)"
    
    if not month_str.isdigit() or not year_str.isdigit():
        return False, "Expiry must contain only digits"
    
    month = int(month_str)
    year = int(year_str)
    
    # Validate month range
    if month < 1 or month > 12:
        return False, "Invalid month (must be 01-12)"
    
    # Check if card has expired
    current_date = datetime.now()
    current_year = current_date.year % 100  # Get last 2 digits of year
    current_month = current_date.month
    
    if year < current_year:
        return False, "Card has expired"
    
    if year == current_year and month < current_month:
        return False, "Card has expired"
    
    return True, ""


def validate_cvv(cvv: str, card_type: str) -> Tuple[bool, str]:
    """
    Validate CVV/CVC code.
    
    Args:
        cvv: CVV code
        card_type: Type of card (for length validation)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cvv.isdigit():
        return False, "CVV must contain only digits"
    
    # American Express uses 4-digit CVV
    if card_type == "amex":
        if len(cvv) != 4:
            return False, "American Express CVV must be 4 digits"
    else:
        # Most cards use 3-digit CVV
        if len(cvv) != 3:
            return False, "CVV must be 3 digits"
    
    return True, ""


def validate_cardholder_name(name: str) -> Tuple[bool, str]:
    """
    Validate cardholder name.
    
    Args:
        name: Cardholder name
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Cardholder name is required"
    
    if len(name.strip()) < 2:
        return False, "Cardholder name must be at least 2 characters"
    
    # Check if name contains at least some letters
    if not any(c.isalpha() for c in name):
        return False, "Cardholder name must contain letters"
    
    return True, ""


def validate_card(card_number: str, cvv: str, expiry: str, cardholder_name: str) -> Tuple[bool, str]:
    """
    Comprehensive card validation.
    
    Args:
        card_number: Card number
        cvv: CVV code
        expiry: Expiry date (MM/YY)
        cardholder_name: Name on card
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Clean card number
    card_clean = card_number.replace(" ", "").replace("-", "")
    
    # Validate card number format
    if not card_clean.isdigit():
        return False, "Card number must contain only digits"
    
    if len(card_clean) < 13 or len(card_clean) > 19:
        return False, "Card number must be between 13-19 digits"
    
    # Validate Luhn checksum
    if not luhn_checksum(card_clean):
        return False, "Invalid card number (failed checksum validation)"
    
    # Get card type
    card_type = get_card_type(card_clean)
    if card_type == "unknown":
        return False, "Card type not recognized. Please use Visa, Mastercard, Amex, or Discover"
    
    # Validate CVV
    cvv_valid, cvv_error = validate_cvv(cvv, card_type)
    if not cvv_valid:
        return False, cvv_error
    
    # Validate expiry
    expiry_valid, expiry_error = validate_expiry(expiry)
    if not expiry_valid:
        return False, expiry_error
    
    # Validate cardholder name
    name_valid, name_error = validate_cardholder_name(cardholder_name)
    if not name_valid:
        return False, name_error
    
    return True, ""


# Test card numbers (pass Luhn validation)
TEST_CARDS = {
    "visa": [
        "4532015112830366",
        "4111111111111111",
        "4532261615902522",
        "4024007198964305"
    ],
    "mastercard": [
        "5425233430109903",
        "5105105105105100",
        "5555555555554444",
        "2221000010000015"
    ],
    "amex": [
        "378282246310005",
        "371449635398431",
        "378734493671000"
    ],
    "discover": [
        "6011111111111117",
        "6011000990139424"
    ]
}


def is_test_card(card_number: str) -> bool:
    """
    Check if card number is a known test card.
    
    Args:
        card_number: Card number (can have spaces/dashes)
    
    Returns:
        True if it's a test card
    """
    card_clean = card_number.replace(" ", "").replace("-", "")
    
    for card_list in TEST_CARDS.values():
        if card_clean in card_list:
            return True
    
    return False
