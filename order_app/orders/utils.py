from datetime import datetime
from decimal import Decimal, InvalidOperation

def safe_decimal_conversion(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None
    
def safe_datetime_conversion(value, date_format, default=None):
    try:
        return datetime.strptime(value, date_format)
    except (TypeError, ValueError):
        return default