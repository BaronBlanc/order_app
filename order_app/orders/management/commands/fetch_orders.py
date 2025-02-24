from decimal import Decimal
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


class Command(BaseCommand):
    help = "Fetch orders from the Lengow XML feed and save them to the database"

    def handle(self, *args, **kwargs):
        url = "http://test.lengow.io/orders-test.xml"
        response = requests.get(url)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("Successfully fetched XML data"))
            xml_data = response.content
            root = ElementTree.fromstring(xml_data)

            for order_elem in root.findall(".//order"):
                order = Order()
                order.marketplace = get_str_from_element_and_xpath(
                    order_elem, "marketplace"
                )
                order.id_flux = get_str_from_element_and_xpath(order_elem, "idFlux")
                order.order_status_marketplace = get_str_from_element_and_xpath(
                    order_elem, ".//marketplace"
                )
                order.order_status_lengow = get_str_from_element_and_xpath(
                    order_elem, ".//lengow"
                )
                order.order_id = get_str_from_element_and_xpath(order_elem, "order_id")
                order.order_mrid = get_str_from_element_and_xpath(
                    order_elem, "order_mrid"
                )
                order.order_refid = get_str_from_element_and_xpath(
                    order_elem, "order_refid"
                )
                order.order_external_id = get_str_from_element_and_xpath(
                    order_elem, "order_external_id"
                )

                # Convert date and time fields to timezone-aware datetimes
                purchase_date = safe_datetime_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_purchase_date"),
                    "%Y-%m-%d",
                )
                order.order_purchase_date = (
                    timezone.make_aware(purchase_date) if purchase_date else None
                )

                purchase_time = safe_datetime_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_purchase_heure"),
                    "%H:%M:%S",
                )
                order.order_purchase_time = (
                    purchase_time.time() if purchase_time else None
                )

                payment_date = safe_datetime_conversion(
                    get_str_from_element_and_xpath(order_elem, ".//payment_date"),
                    "%Y-%m-%d",
                )
                order.payment_date = (
                    timezone.make_aware(payment_date) if payment_date else None
                )

                payment_time = safe_datetime_conversion(
                    get_str_from_element_and_xpath(order_elem, ".//payment_heure"),
                    "%H:%M:%S",
                )
                order.payment_time = payment_time.time() if payment_time else None

                shipped_date = safe_datetime_conversion(
                    get_str_from_element_and_xpath(
                        order_elem, ".//tracking_shipped_date"
                    ),
                    "%Y-%m-%d %H:%M:%S",
                )
                order.tracking_shipped_date = (
                    timezone.make_aware(shipped_date) if shipped_date else None
                )

                # Convert decimal fields
                order.order_amount = safe_decimal_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_amount")
                )
                order.order_tax = safe_decimal_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_tax")
                )
                order.order_shipping = safe_decimal_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_shipping")
                )
                order.order_commission = safe_decimal_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_commission")
                )
                order.order_processing_fee = safe_decimal_conversion(
                    get_str_from_element_and_xpath(order_elem, "order_processing_fee")
                )
                order.tracking_parcel_weight = (
                    safe_decimal_conversion(
                        get_str_from_element_and_xpath(
                            order_elem, ".//tracking_parcel_weight"
                        )
                    )
                    if get_str_from_element_and_xpath(
                        order_elem, ".//tracking_parcel_weight"
                    )
                    else Decimal(0.0)
                )

                # Set other fields
                order.order_items = get_str_from_element_and_xpath(
                    order_elem, ".//order_items"
                )
                order.order_currency = get_str_from_element_and_xpath(
                    order_elem, "order_currency"
                )
                order.payment_checkout = get_str_from_element_and_xpath(
                    order_elem, ".//payment_checkout"
                )
                order.payment_status = get_str_from_element_and_xpath(
                    order_elem, ".//payment_status"
                )
                order.payment_type = get_str_from_element_and_xpath(
                    order_elem, ".//payment_type"
                )
                order.invoice_number = get_str_from_element_and_xpath(
                    order_elem, ".//invoice_number"
                )
                order.invoice_url = get_str_from_element_and_xpath(
                    order_elem, ".//invoice_url"
                )
                order.billing_society = get_str_from_element_and_xpath(
                    order_elem, ".//billing_society"
                )
                order.billing_civility = get_str_from_element_and_xpath(
                    order_elem, ".//billing_civility"
                )
                order.billing_lastname = get_str_from_element_and_xpath(
                    order_elem, ".//billing_lastname"
                )
                order.billing_firstname = get_str_from_element_and_xpath(
                    order_elem, ".//billing_firstname"
                )
                order.billing_email = get_str_from_element_and_xpath(
                    order_elem, ".//billing_email"
                )
                order.billing_address = get_str_from_element_and_xpath(
                    order_elem, "./billing_address/billing_address"
                )
                order.billing_address_2 = get_str_from_element_and_xpath(
                    order_elem, ".//billing_address_2"
                )
                order.billing_address_complement = get_str_from_element_and_xpath(
                    order_elem, ".//billing_address_complement"
                )
                order.billing_zipcode = get_str_from_element_and_xpath(
                    order_elem, ".//billing_zipcode"
                )
                order.billing_city = get_str_from_element_and_xpath(
                    order_elem, ".//billing_city"
                )
                order.billing_country = get_str_from_element_and_xpath(
                    order_elem, ".//billing_country"
                )
                order.billing_country_iso = get_str_from_element_and_xpath(
                    order_elem, ".//billing_country_iso"
                )
                order.billing_phone_home = get_str_from_element_and_xpath(
                    order_elem, ".//billing_phone_home"
                )
                order.billing_phone_office = get_str_from_element_and_xpath(
                    order_elem, ".//billing_phone_office"
                )
                order.billing_phone_mobile = get_str_from_element_and_xpath(
                    order_elem, ".//billing_phone_mobile"
                )
                order.billing_full_address = get_str_from_element_and_xpath(
                    order_elem, ".//billing_full_address"
                )
                order.delivery_society = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_society"
                )
                order.delivery_civility = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_civility"
                )
                order.delivery_lastname = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_lastname"
                )
                order.delivery_firstname = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_firstname"
                )
                order.delivery_email = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_email"
                )
                order.delivery_address = get_str_from_element_and_xpath(
                    order_elem, "./delivery_address/delivery_address"
                )
                order.delivery_address_2 = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_address_2"
                )
                order.delivery_address_complement = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_address_complement"
                )
                order.delivery_zipcode = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_zipcode"
                )
                order.delivery_city = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_city"
                )
                order.delivery_country = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_country"
                )
                order.delivery_country_iso = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_country_iso"
                )
                order.delivery_phone_home = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_phone_home"
                )
                order.delivery_phone_office = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_phone_office"
                )
                order.delivery_phone_mobile = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_phone_mobile"
                )
                order.delivery_full_address = get_str_from_element_and_xpath(
                    order_elem, ".//delivery_full_address"
                )
                order.tracking_method = get_str_from_element_and_xpath(
                    order_elem, ".//tracking_method"
                )
                order.tracking_carrier = get_str_from_element_and_xpath(
                    order_elem, ".//tracking_carrier"
                )
                order.tracking_number = get_str_from_element_and_xpath(
                    order_elem, ".//tracking_number"
                )
                order.tracking_url = get_str_from_element_and_xpath(
                    order_elem, ".//tracking_url"
                )
                order.tracking_relay = get_str_from_element_and_xpath(
                    order_elem, ".//tracking_relay"
                )
                order.tracking_delivering_by_marketplace = (
                    get_str_from_element_and_xpath(
                        order_elem, ".//tracking_deliveringByMarketPlace"
                    )
                    == "1"
                )
                order.order_comments = get_str_from_element_and_xpath(
                    order_elem, ".//order_comments"
                )
                order.customer_id = get_str_from_element_and_xpath(
                    order_elem, ".//customer_id"
                )

                order.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully created order {order.order_id}")
                )

        else:
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch data = {response.status_code}")
            )
