from decimal import Decimal
import logging
from xml.etree import ElementTree
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order
from orders.utils import (
    get_str_from_element_and_xpath,
    safe_datetime_conversion,
    safe_decimal_conversion,
)

logger = logging.getLogger(__name__)

field_mappings = {
    "marketplace": "marketplace",
    "id_flux": "idFlux",
    "order_status_marketplace": ".//marketplace",
    "order_status_lengow": ".//lengow",
    "order_id": "order_id",
    "order_mrid": "order_mrid",
    "order_refid": "order_refid",
    "order_external_id": "order_external_id",
    "order_currency": "order_currency",
    "payment_checkout": ".//payment_checkout",
    "payment_status": ".//payment_status",
    "payment_type": ".//payment_type",
    "invoice_number": ".//invoice_number",
    "invoice_url": ".//invoice_url",
    "billing_society": ".//billing_society",
    "billing_civility": ".//billing_civility",
    "billing_lastname": ".//billing_lastname",
    "billing_firstname": ".//billing_firstname",
    "billing_email": ".//billing_email",
    "billing_address": "./billing_address/billing_address",
    "billing_address_2": ".//billing_address_2",
    "billing_address_complement": ".//billing_address_complement",
    "billing_zipcode": ".//billing_zipcode",
    "billing_city": ".//billing_city",
    "billing_country": ".//billing_country",
    "billing_country_iso": ".//billing_country_iso",
    "billing_phone_home": ".//billing_phone_home",
    "billing_phone_office": ".//billing_phone_office",
    "billing_phone_mobile": ".//billing_phone_mobile",
    "billing_full_address": ".//billing_full_address",
    "delivery_society": ".//delivery_society",
    "delivery_civility": ".//delivery_civility",
    "delivery_lastname": ".//delivery_lastname",
    "delivery_firstname": ".//delivery_firstname",
    "delivery_email": ".//delivery_email",
    "delivery_address": "./delivery_address/delivery_address",
    "delivery_address_2": ".//delivery_address_2",
    "delivery_address_complement": ".//delivery_address_complement",
    "delivery_zipcode": ".//delivery_zipcode",
    "delivery_city": ".//delivery_city",
    "delivery_country": ".//delivery_country",
    "delivery_country_iso": ".//delivery_country_iso",
    "delivery_phone_home": ".//delivery_phone_home",
    "delivery_phone_office": ".//delivery_phone_office",
    "delivery_phone_mobile": ".//delivery_phone_mobile",
    "delivery_full_address": ".//delivery_full_address",
    "tracking_method": ".//tracking_method",
    "tracking_carrier": ".//tracking_carrier",
    "tracking_number": ".//tracking_number",
    "tracking_url": ".//tracking_url",
    "tracking_relay": ".//tracking_relay",
    "order_comments": ".//order_comments",
    "customer_id": ".//customer_id",
}

date_fields = {
    "order_purchase_date": ("order_purchase_date", "%Y-%m-%d"),
    "order_purchase_time": ("order_purchase_heure", "%H:%M:%S"),
    "payment_date": (".//payment_date", "%Y-%m-%d"),
    "payment_time": (".//payment_heure", "%H:%M:%S"),
    "tracking_shipped_date": (".//tracking_shipped_date", "%Y-%m-%d %H:%M:%S"),
}

decimal_fields = [
    "order_amount",
    "order_tax",
    "order_shipping",
    "order_commission",
    "order_processing_fee",
    "tracking_parcel_weight",
]


class Command(BaseCommand):
    help = "Fetch orders from the Lengow XML feed and save them to the database"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL of the remote XML feed")

    def handle(self, *args, **kwargs):
        url = (
            kwargs["url"] if kwargs["url"] else "http://test.lengow.io/orders-test.xml"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad HTTP status codes
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data: {e}")
            return

        xml_data = response.content
        logger.info("Successfully fetched XML data")
        root = ElementTree.fromstring(xml_data)

        for order_elem in root.findall(".//order"):
            try:
                order = Order()

                for field, xpath in field_mappings.items():
                    setattr(
                        order, field, get_str_from_element_and_xpath(order_elem, xpath)
                    )

                for field, (xpath, date_format) in date_fields.items():
                    date_value = safe_datetime_conversion(
                        get_str_from_element_and_xpath(order_elem, xpath), date_format
                    )
                    if date_value:
                        if "time" in field:
                            setattr(order, field, date_value.time())
                        else:
                            setattr(order, field, timezone.make_aware(date_value))

                for field in decimal_fields:
                    setattr(
                        order,
                        field,
                        safe_decimal_conversion(
                            get_str_from_element_and_xpath(order_elem, field)
                        )
                        or Decimal(0.0),
                    )

                order.tracking_delivering_by_marketplace = (
                    get_str_from_element_and_xpath(
                        order_elem, ".//tracking_deliveringByMarketPlace"
                    )
                    == "1"
                )

                order.save()
                logger.info(f"Successfully created order {order.order_id}")

            except Exception as e:
                logger.error(f"Failed to process order: {e}")
                break
