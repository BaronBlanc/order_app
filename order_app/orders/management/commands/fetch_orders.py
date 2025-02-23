import requests
from django.core.management.base import BaseCommand
from xml.etree import ElementTree
from orders.models import Order
from datetime import datetime
from django.utils import timezone
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

class Command(BaseCommand):
    help = 'Fetch orders from the Lengow XML feed and save them to the database'

    def handle(self, *args, **kwargs):
        url = 'http://test.lengow.io/orders-test.xml'
        response = requests.get(url)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('Successfully fetched XML data'))
            xml_data = response.content
            root = ElementTree.fromstring(xml_data)

            for order_elem in root.findall('.//order'):
                order = Order()
                order.marketplace = order_elem.find('marketplace').text
                order.id_flux = order_elem.find('idFlux').text
                order.order_status_marketplace = order_elem.find('.//marketplace').text
                order.order_status_lengow = order_elem.find('.//lengow').text
                order.order_id = order_elem.find('order_id').text
                order.order_mrid = order_elem.find('order_mrid').text
                order.order_refid = order_elem.find('order_refid').text
                order.order_external_id = order_elem.find('order_external_id').text or ''

                # Convert date and time fields to timezone-aware datetimes
                purchase_date = safe_datetime_conversion(order_elem.find('order_purchase_date').text, '%Y-%m-%d')
                order.order_purchase_date = timezone.make_aware(purchase_date) if purchase_date else None

                purchase_time = safe_datetime_conversion(order_elem.find('order_purchase_heure').text, '%H:%M:%S')
                order.order_purchase_time = purchase_time.time() if purchase_time else None

                payment_date = safe_datetime_conversion(order_elem.find('.//payment_date').text, '%Y-%m-%d')
                order.payment_date = timezone.make_aware(payment_date) if payment_date else None

                payment_time = safe_datetime_conversion(order_elem.find('.//payment_heure').text, '%H:%M:%S')
                order.payment_time = payment_time.time() if payment_time else None

                shipped_date = safe_datetime_conversion(order_elem.find('.//tracking_shipped_date').text, '%Y-%m-%d %H:%M:%S')
                order.tracking_shipped_date = timezone.make_aware(shipped_date) if shipped_date else None

                # Convert decimal fields
                order.order_amount = safe_decimal_conversion(order_elem.find('order_amount').text)
                order.order_tax = safe_decimal_conversion(order_elem.find('order_tax').text) 
                order.order_shipping = safe_decimal_conversion(order_elem.find('order_shipping').text)
                order.order_commission = safe_decimal_conversion(order_elem.find('order_commission').text)
                order.order_processing_fee = safe_decimal_conversion(order_elem.find('order_processing_fee').text)
                order.tracking_parcel_weight = safe_decimal_conversion(order_elem.find('.//tracking_parcel_weight').text) if order_elem.find('.//tracking_parcel_weight').text else Decimal(0.0)

                # Set other fields
                order.order_items = order_elem.find('.//order_items').text
                order.order_currency = order_elem.find('order_currency').text
                order.payment_checkout = order_elem.find('.//payment_checkout').text or ''
                order.payment_status = order_elem.find('.//payment_status').text or ''
                order.payment_type = order_elem.find('.//payment_type').text or ''
                order.invoice_number = order_elem.find('.//invoice_number').text or ''
                order.invoice_url = order_elem.find('.//invoice_url').text or ''
                order.billing_society = order_elem.find('.//billing_society').text or ''
                order.billing_civility = order_elem.find('.//billing_civility').text or ''
                order.billing_lastname = order_elem.find('.//billing_lastname').text
                order.billing_firstname = order_elem.find('.//billing_firstname').text or ''
                order.billing_email = order_elem.find('.//billing_email').text
                order.billing_address = order_elem.find('.//billing_address').text
                order.billing_address_2 = order_elem.find('.//billing_address_2').text or ''
                order.billing_address_complement = order_elem.find('.//billing_address_complement').text or ''
                order.billing_zipcode = order_elem.find('.//billing_zipcode').text
                order.billing_city = order_elem.find('.//billing_city').text
                order.billing_country = order_elem.find('.//billing_country').text
                order.billing_country_iso = order_elem.find('.//billing_country_iso').text
                order.billing_phone_home = order_elem.find('.//billing_phone_home').text or ''
                order.billing_phone_office = order_elem.find('.//billing_phone_office').text or ''
                order.billing_phone_mobile = order_elem.find('.//billing_phone_mobile').text or ''
                order.billing_full_address = order_elem.find('.//billing_full_address').text
                order.delivery_society = order_elem.find('.//delivery_society').text or ''
                order.delivery_civility = order_elem.find('.//delivery_civility').text or ''
                order.delivery_lastname = order_elem.find('.//delivery_lastname').text or ''
                order.delivery_firstname = order_elem.find('.//delivery_firstname').text or ''
                order.delivery_email = order_elem.find('.//delivery_email').text or ''
                order.delivery_address = order_elem.find('.//delivery_address').text
                order.delivery_address_2 = order_elem.find('.//delivery_address_2').text or ''
                order.delivery_address_complement = order_elem.find('.//delivery_address_complement').text or ''
                order.delivery_zipcode = order_elem.find('.//delivery_zipcode').text
                order.delivery_city = order_elem.find('.//delivery_city').text
                order.delivery_country = order_elem.find('.//delivery_country').text
                order.delivery_country_iso = order_elem.find('.//delivery_country_iso').text
                order.delivery_phone_home = order_elem.find('.//delivery_phone_home').text or ''
                order.delivery_phone_office = order_elem.find('.//delivery_phone_office').text or ''
                order.delivery_phone_mobile = order_elem.find('.//delivery_phone_mobile').text or ''
                order.delivery_full_address = order_elem.find('.//delivery_full_address').text
                order.tracking_method = order_elem.find('.//tracking_method').text or ''
                order.tracking_carrier = order_elem.find('.//tracking_carrier').text or ''
                order.tracking_number = order_elem.find('.//tracking_number').text or ''
                order.tracking_url = order_elem.find('.//tracking_url').text or ''
                order.tracking_relay = order_elem.find('.//tracking_relay').text or ''
                order.tracking_delivering_by_marketplace = order_elem.find('.//tracking_deliveringByMarketPlace').text == '1'
                order.order_comments = order_elem.find('.//order_comments').text or ''
                order.customer_id = order_elem.find('.//customer_id').text or ''
                order.order_ip = order_elem.find('.//order_ip').text or ''

                order.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully created order {order.order_id}'))

        else:
            self.stdout.write(self.style.ERROR(f'Failed to fetch XML data = {response.status_code}'))
