import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from xml.etree import ElementTree

import requests
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from orders.models import Order
from orders.utils import (
    get_str_from_element_and_xpath,
    safe_datetime_conversion,
    safe_decimal_conversion,
)

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIRS = os.path.join(PROJECT_ROOT, "fixtures")


def load_fixture(filename):
    with open(os.path.join(FIXTURE_DIRS, filename), "r", encoding="utf-8") as file:
        return file.read()


class TestUtils(TestCase):
    def test_safe_decimal_conversion_valid(self):
        self.assertEqual(safe_decimal_conversion("10.5"), Decimal("10.5"))
        self.assertEqual(safe_decimal_conversion(10.5), Decimal("10.5"))
        self.assertEqual(safe_decimal_conversion(10), Decimal("10"))

    def test_safe_decimal_conversion_invalid(self):
        self.assertIsNone(safe_decimal_conversion("invalid"))
        self.assertIsNone(safe_decimal_conversion(None))
        self.assertIsNone(safe_decimal_conversion(""))

    def test_safe_datetime_conversion_valid(self):
        self.assertEqual(
            safe_datetime_conversion("2023-10-05", "%Y-%m-%d"), datetime(2023, 10, 5)
        )
        self.assertEqual(
            safe_datetime_conversion("05/10/2023", "%d/%m/%Y"), datetime(2023, 10, 5)
        )

    def test_safe_datetime_conversion_invalid(self):
        self.assertIsNone(safe_datetime_conversion("invalid", "%Y-%m-%d"))
        self.assertIsNone(safe_datetime_conversion(None, "%Y-%m-%d"))
        self.assertIsNone(safe_datetime_conversion("", "%Y-%m-%d"))

    def test_safe_datetime_conversion_default(self):
        default_date = datetime(2023, 1, 1)
        self.assertEqual(
            safe_datetime_conversion("invalid", "%Y-%m-%d", default=default_date),
            default_date,
        )
        self.assertEqual(
            safe_datetime_conversion(None, "%Y-%m-%d", default=default_date),
            default_date,
        )
        self.assertEqual(
            safe_datetime_conversion("", "%Y-%m-%d", default=default_date), default_date
        )

    def test_get_str_from_element_and_xpath_element_found_with_text(self):
        element = ElementTree.fromstring(load_fixture("simple_xml_model.xml"))
        result = get_str_from_element_and_xpath(element, "child")
        self.assertEqual(result, "test")

    def test_get_str_from_element_and_xpath_element_found_without_text(self):
        element = ElementTree.fromstring(
            load_fixture("simple_xml_model_no_children.xml")
        )
        result = get_str_from_element_and_xpath(element, "child")
        self.assertEqual(result, "")

    def test_get_str_from_element_and_xpath_element_not_found(self):
        element = ElementTree.fromstring(load_fixture("simple_xml_model.xml"))
        result = get_str_from_element_and_xpath(element, "nonexistent")
        self.assertEqual(result, "")

    def test_get_str_from_billing_address(self):
        element = ElementTree.fromstring(load_fixture("xml_billing_address.xml"))
        result = get_str_from_element_and_xpath(element, ".//billing_address")
        self.assertEqual(result, "014 rue de la poupée")


class FetchOrdersCommandTest(TestCase):
    @patch("requests.get")
    def test_fetch_orders_command(self, mock_get):
        # Mock the response from the requests.get call
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = load_fixture("xml_full_orders_lengow.xml")
        # mock_response._content = mock_response._content.encode('windows-1252')
        mock_get.return_value = mock_response

        # Call the management command
        call_command("fetch_orders", "test")

        # Verify that the orders were created correctly
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.marketplace, "amazon")
        self.assertEqual(order.order_id, "111-2222222-3333333")
        self.assertEqual(order.order_amount, Decimal("34.5"))
        self.assertEqual(order.order_tax, Decimal("0"))
        self.assertEqual(order.order_shipping, Decimal("5.5"))
        self.assertEqual(order.order_currency, "EUR")
        self.assertEqual(order.billing_lastname, "Tom Croisière")
        self.assertEqual(order.billing_address, "014 rue de la poupée")
        self.assertEqual(order.billing_zipcode, "75000")
        self.assertEqual(order.billing_city, "Paris")
        self.assertEqual(order.billing_country, "FR")
        self.assertEqual(order.billing_country_iso, "FR")
        self.assertEqual(order.billing_phone_home, "0605050404")
        self.assertEqual(order.delivery_address, "014 rue de la poupée")
        self.assertEqual(order.delivery_zipcode, "75000")
        self.assertEqual(order.delivery_city, "Paris")
        self.assertEqual(order.delivery_country, "FR")
        self.assertEqual(order.delivery_country_iso, "FR")
        self.assertEqual(order.delivery_phone_home, "0605040102")
        self.assertEqual(order.tracking_carrier, "Standard")
        self.assertEqual(
            order.tracking_shipped_date,
            timezone.make_aware(datetime(2015, 1, 20, 16, 1, 1)),
        )
        self.assertEqual(order.tracking_method, "")
        self.assertEqual(order.tracking_number, "")
        self.assertEqual(order.tracking_url, "")
        self.assertEqual(order.tracking_relay, "")
        self.assertEqual(order.tracking_delivering_by_marketplace, False)
        self.assertEqual(order.order_comments, "")
        self.assertEqual(order.customer_id, "")
