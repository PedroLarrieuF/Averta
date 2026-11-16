"""Helper functions for the automation."""

import re
import hashlib
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from slugify import slugify
import phonenumbers
from email_validator import validate_email, EmailNotValidError


def generate_id(*args: str) -> str:
    """Generate a unique ID from string arguments."""
    combined = "|".join(str(arg) for arg in args)
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def clean_string(text: Optional[str]) -> Optional[str]:
    """Clean and normalize a string."""
    if not text:
        return None
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-\.\,\@\(\)\/]', '', text)
    return text if text else None


def normalize_phone(phone: str, country: str = "BR") -> Optional[str]:
    """Normalize phone number to E.164 format."""
    if not phone:
        return None

    try:
        parsed = phonenumbers.parse(phone, country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass

    # Try to clean and parse again
    cleaned = re.sub(r'[^\d\+]', '', phone)
    try:
        parsed = phonenumbers.parse(cleaned, country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass

    return None


def is_valid_email(email: str) -> bool:
    """Validate email address."""
    if not email:
        return False
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def normalize_email(email: str) -> Optional[str]:
    """Normalize and validate email."""
    if not email:
        return None
    email = email.strip().lower()
    if is_valid_email(email):
        return email
    return None


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    if not url:
        return None
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    # Remove www
    url = re.sub(r'^www\.', '', url)
    # Get domain part
    domain = url.split('/')[0].split(':')[0]
    return domain.lower() if domain else None


def is_business_email(email: str) -> bool:
    """Check if email appears to be a business email (not generic)."""
    if not email:
        return False

    generic_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'live.com', 'msn.com', 'icloud.com', 'aol.com',
        'bol.com.br', 'uol.com.br', 'terra.com.br', 'ig.com.br',
        'r7.com', 'globo.com', 'yahoo.com.br', 'hotmail.com.br'
    }

    domain = extract_domain(email)
    return domain not in generic_domains if domain else False


def parse_address(address: str) -> Dict[str, Optional[str]]:
    """Parse Brazilian address into components."""
    result = {
        'street': None,
        'number': None,
        'complement': None,
        'neighborhood': None,
        'city': None,
        'state': None,
        'postal_code': None,
        'country': 'Brasil'
    }

    if not address:
        return result

    # Extract CEP
    cep_match = re.search(r'\b(\d{5}-?\d{3})\b', address)
    if cep_match:
        result['postal_code'] = cep_match.group(1)
        address = address.replace(cep_match.group(0), '').strip()

    # Extract state (UF)
    states = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    for state in states:
        pattern = rf'\b{state}\b'
        if re.search(pattern, address, re.IGNORECASE):
            result['state'] = state
            break

    return result


def slugify_text(text: str) -> str:
    """Create a slug from text."""
    return slugify(text, lowercase=True, separator='_')


def format_date(dt: Optional[Union[datetime, date]] = None, fmt: str = "%Y-%m-%d") -> str:
    """Format date as string."""
    if dt is None:
        dt = datetime.now()
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return dt.strftime(fmt)


def parse_json_field(value: Any) -> Any:
    """Parse JSON field from database."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def serialize_json_field(value: Any) -> Optional[str]:
    """Serialize value to JSON string for database."""
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(d: Dict, *keys, default=None) -> Any:
    """Safely get nested dictionary value."""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries, later values override earlier."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_none_values(d: Dict) -> Dict:
    """Remove None values from dictionary."""
    return {k: v for k, v in d.items() if v is not None}


def truncate_string(text: str, max_length: int = 255, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def format_currency(value: Union[int, float], currency: str = "BRL") -> str:
    """Format currency value."""
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{currency} {value:,.2f}"


def get_brazil_state_name(code: str) -> Optional[str]:
    """Get full state name from code."""
    states = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    return states.get(code.upper())


def is_brazil_holiday(dt: date) -> bool:
    """Check if date is a Brazilian national holiday (simplified)."""
    # Fixed holidays
    fixed_holidays = [
        (1, 1),   # Confraternização Universal
        (4, 21),  # Tiradentes
        (5, 1),   # Dia do Trabalhador
        (9, 7),   # Independência do Brasil
        (10, 12), # Nossa Senhora Aparecida
        (11, 2),  # Finados
        (11, 15), # Proclamação da República
        (12, 25), # Natal
    ]

    return (dt.month, dt.day) in fixed_holidays


def is_business_day(dt: date) -> bool:
    """Check if date is a business day (Mon-Fri, not holiday)."""
    if dt.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return not is_brazil_holiday(dt)


def get_next_business_day(dt: date) -> date:
    """Get next business day."""
    next_day = dt
    while True:
        next_day = date.fromordinal(next_day.toordinal() + 1)
        if is_business_day(next_day):
            return next_day