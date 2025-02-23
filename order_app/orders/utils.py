from datetime import datetime
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree

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
    
def get_str_from_element_and_xpath(element: ElementTree.Element, xpath: str) -> str:
    found_element = element.find(xpath)
    if found_element is not None:
        return found_element.text.replace('\u00A0', ' ').strip() if found_element.text else ''
    else:
        return ''
