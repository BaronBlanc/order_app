from datetime import datetime
from xml.etree.ElementTree import ElementTree, fromstring
from django.test import TestCase
from orders.utils import get_str_from_element_and_xpath, safe_datetime_conversion, safe_decimal_conversion
import requests
from django.core.management import call_command
from unittest.mock import patch
from orders.models import Order
from django.utils import timezone
from decimal import Decimal

class TestUtils(TestCase):

    def test_safe_decimal_conversion_valid(self):
        self.assertEqual(safe_decimal_conversion('10.5'), Decimal('10.5'))
        self.assertEqual(safe_decimal_conversion(10.5), Decimal('10.5'))
        self.assertEqual(safe_decimal_conversion(10), Decimal('10'))

    def test_safe_decimal_conversion_invalid(self):
        self.assertIsNone(safe_decimal_conversion('invalid'))
        self.assertIsNone(safe_decimal_conversion(None))
        self.assertIsNone(safe_decimal_conversion(''))

    def test_safe_datetime_conversion_valid(self):
        self.assertEqual(safe_datetime_conversion('2023-10-05', '%Y-%m-%d'), datetime(2023, 10, 5))
        self.assertEqual(safe_datetime_conversion('05/10/2023', '%d/%m/%Y'), datetime(2023, 10, 5))

    def test_safe_datetime_conversion_invalid(self):
        self.assertIsNone(safe_datetime_conversion('invalid', '%Y-%m-%d'))
        self.assertIsNone(safe_datetime_conversion(None, '%Y-%m-%d'))
        self.assertIsNone(safe_datetime_conversion('', '%Y-%m-%d'))

    def test_safe_datetime_conversion_default(self):
        default_date = datetime(2023, 1, 1)
        self.assertEqual(safe_datetime_conversion('invalid', '%Y-%m-%d', default=default_date), default_date)
        self.assertEqual(safe_datetime_conversion(None, '%Y-%m-%d', default=default_date), default_date)
        self.assertEqual(safe_datetime_conversion('', '%Y-%m-%d', default=default_date), default_date)

    def test_get_str_from_element_and_xpath_element_found_with_text(self):
        xml_string = '<root><child>test</child></root>'
        element = fromstring(xml_string)
        result = get_str_from_element_and_xpath(element, 'child')
        self.assertEqual(result, 'test')

    def test_get_str_from_element_and_xpath_element_found_without_text(self):
        xml_string = '<root><child></child></root>'
        element = fromstring(xml_string)
        result = get_str_from_element_and_xpath(element, 'child')
        self.assertEqual(result, '')

    def test_get_str_from_element_and_xpath_element_not_found(self):
        xml_string = '<root><child>test</child></root>'
        element = fromstring(xml_string)
        result = get_str_from_element_and_xpath(element, 'nonexistent')
        self.assertEqual(result, '')

    def test_get_str_from_element_and_xpath_element_with_whitespace_text(self):
        xml_string = '<root><child>  test  </child></root>'
        element = fromstring(xml_string)
        result = get_str_from_element_and_xpath(element, 'child')
        self.assertEqual(result, 'test')
    
    def test_get_str_from_billing_address(self):
        xml_string = '''<billing_address>
                        <billing_society><![CDATA[]]></billing_society>
                        <billing_civility><![CDATA[]]></billing_civility>
                        <billing_lastname><![CDATA[Tom Croisière]]></billing_lastname>
                        <billing_firstname><![CDATA[]]></billing_firstname>
                        <billing_email><![CDATA[web1n0r@marketplace.amazon.fr]]></billing_email>
                        <billing_address><![CDATA[014 rue de la poupée]]></billing_address>
                        <billing_address_2><![CDATA[]]></billing_address_2>
                        <billing_address_complement><![CDATA[]]></billing_address_complement>
                        <billing_zipcode><![CDATA[75000]]></billing_zipcode>
                        <billing_city><![CDATA[Paris]]></billing_city>
                        <billing_country><![CDATA[FR]]></billing_country>
                        <billing_country_iso><![CDATA[FR]]></billing_country_iso>
                        <billing_phone_home><![CDATA[0605050404]]></billing_phone_home>
                        <billing_phone_office><![CDATA[]]></billing_phone_office>
                        <billing_phone_mobile><![CDATA[]]></billing_phone_mobile>
                        <billing_full_address><![CDATA[014 rue de la poupée   75000 Paris FR]]></billing_full_address>
                    </billing_address>'''
        element = fromstring(xml_string)
        result = get_str_from_element_and_xpath(element, './/billing_address')
        self.assertEqual(result, '014 rue de la poupée')

class FetchOrdersCommandTest(TestCase):
  
    def get_xml_response(self) -> str: 
        return '''<?xml version="1.0" encoding="windows-1252"?>
        <statistics ip="xx.xx.xx.xx" server="LengowTest" timeGenerated="2015-07-01 00:00:00.652336" version="2.1">
            <orders_count>
                <count_total>5</count_total>
                <count_by_marketplace>
                    <cdiscount>2</cdiscount>
                    <amazon>3</amazon>
                </count_by_marketplace>
                <count_by_status>
                    <cancel>0</cancel>
                    <new>1</new>
                    <shipped>0</shipped>
                    <processing>3</processing>
                </count_by_status>
            </orders_count>
            <orders>
                <order>
                    <marketplace><![CDATA[amazon]]></marketplace>
                    <idFlux><![CDATA[88827]]></idFlux>
                    <order_status>
                        <marketplace><![CDATA[accept]]></marketplace>
                        <lengow><![CDATA[processing]]></lengow>
                    </order_status>
                    <order_id><![CDATA[111-2222222-3333333]]></order_id>
                    <order_mrid><![CDATA[111-2222222-3333333]]></order_mrid>
                    <order_refid><![CDATA[111-2222222-3333333]]></order_refid>
                    <order_external_id><![CDATA[]]></order_external_id>
                    <order_purchase_date><![CDATA[2014-10-21]]></order_purchase_date>
                    <order_purchase_heure><![CDATA[14:59:51]]></order_purchase_heure>
                    <order_amount><![CDATA[34.5]]></order_amount>
                    <order_tax><![CDATA[0]]></order_tax>
                    <order_shipping><![CDATA[5.5]]></order_shipping>
                    <order_commission><![CDATA[0.0]]></order_commission>
                    <order_processing_fee><![CDATA[0]]></order_processing_fee>
                    <order_currency><![CDATA[EUR]]></order_currency>
                    <order_payment>
                        <payment_checkout><![CDATA[]]></payment_checkout>
                        <payment_status><![CDATA[]]></payment_status>
                        <payment_type><![CDATA[]]></payment_type>
                        <payment_date><![CDATA[2014-10-21]]></payment_date>
                        <payment_heure><![CDATA[14:59:51]]></payment_heure>
                    </order_payment>
                    <order_invoice>
                        <invoice_number><![CDATA[]]></invoice_number>
                        <invoice_url><![CDATA[]]></invoice_url>
                    </order_invoice>
                    <billing_address>
                        <billing_society><![CDATA[]]></billing_society>
                        <billing_civility><![CDATA[]]></billing_civility>
                        <billing_lastname><![CDATA[Tom Croisière]]></billing_lastname>
                        <billing_firstname><![CDATA[]]></billing_firstname>
                        <billing_email><![CDATA[web1n0r@marketplace.amazon.fr]]></billing_email>
                        <billing_address><![CDATA[014 rue de la poupée]]></billing_address>
                        <billing_address_2><![CDATA[]]></billing_address_2>
                        <billing_address_complement><![CDATA[]]></billing_address_complement>
                        <billing_zipcode><![CDATA[75000]]></billing_zipcode>
                        <billing_city><![CDATA[Paris]]></billing_city>
                        <billing_country><![CDATA[FR]]></billing_country>
                        <billing_country_iso><![CDATA[FR]]></billing_country_iso>
                        <billing_phone_home><![CDATA[0605050404]]></billing_phone_home>
                        <billing_phone_office><![CDATA[]]></billing_phone_office>
                        <billing_phone_mobile><![CDATA[]]></billing_phone_mobile>
                        <billing_full_address><![CDATA[014 rue de la poupée   75000 Paris FR]]></billing_full_address>
                    </billing_address>
                    <delivery_address>
                        <delivery_society><![CDATA[]]></delivery_society>
                        <delivery_civility><![CDATA[]]></delivery_civility>
                        <delivery_lastname><![CDATA[]]></delivery_lastname>
                        <delivery_firstname><![CDATA[]]></delivery_firstname>
                        <delivery_email><![CDATA[]]></delivery_email>
                        <delivery_address><![CDATA[014 rue de la poupée]]></delivery_address>
                        <delivery_address_2><![CDATA[]]></delivery_address_2>
                        <delivery_address_complement><![CDATA[]]></delivery_address_complement>
                        <delivery_zipcode><![CDATA[75000]]></delivery_zipcode>
                        <delivery_city><![CDATA[Paris]]></delivery_city>
                        <delivery_country><![CDATA[FR]]></delivery_country>
                        <delivery_country_iso><![CDATA[FR]]></delivery_country_iso>
                        <delivery_phone_home><![CDATA[0605040102]]></delivery_phone_home>
                        <delivery_phone_office><![CDATA[]]></delivery_phone_office>
                        <delivery_phone_mobile><![CDATA[]]></delivery_phone_mobile>
                        <delivery_full_address><![CDATA[014 rue de la poupée   75000 Paris FR]]></delivery_full_address>
                    </delivery_address>
                    <tracking_informations>
                        <tracking_method><![CDATA[]]></tracking_method>
                        <tracking_carrier><![CDATA[Standard]]></tracking_carrier>
                        <tracking_number><![CDATA[]]></tracking_number>
                        <tracking_url><![CDATA[]]></tracking_url>
                        <tracking_shipped_date><![CDATA[2015-01-20 16:01:01]]></tracking_shipped_date>
                        <tracking_relay><![CDATA[]]></tracking_relay>
                        <tracking_deliveringByMarketPlace><![CDATA[0]]></tracking_deliveringByMarketPlace>
                        <tracking_parcel_weight><![CDATA[]]></tracking_parcel_weight>
                    </tracking_informations>
                    <order_comments><![CDATA[]]></order_comments>
                    <customer_id><![CDATA[]]></customer_id>
                    <order_ip><![CDATA[]]></order_ip>
                    <order_items><![CDATA[1]]></order_items>
                    <cart>
                        <nb_orders>1</nb_orders>
                        <products>
                            <product>
                                <idLengow><![CDATA[114526]]></idLengow>
                                <idMP><![CDATA[114526]]></idMP>
                                <sku field="Identifiant_unique"><![CDATA[11_12]]></sku>
                                <ean><![CDATA[]]></ean>
                                <title><![CDATA[T-Shirt  col rond]]></title>
                                <category><![CDATA[Vetements Femmes > Tee-shirts]]></category>
                                <brand><![CDATA[]]></brand>
                                <url_product><![CDATA[]]></url_product>
                                <url_image><![CDATA[http://brain.pan.e-merchant.com/3/7/12313673/l_12313673.jpg]]></url_image>
                                <order_lineid><![CDATA[]]></order_lineid>
                                <quantity><![CDATA[1]]></quantity>
                                <price><![CDATA[29.0]]></price>
                                <price_unit><![CDATA[29.0]]></price_unit>
                                <shipping_price><![CDATA[]]></shipping_price>
                                <tax><![CDATA[]]></tax>
                                <status><![CDATA[]]></status>
                            </product>
                        </products>
                    </cart>
                </order>
            </orders>
        </statistics>'''

    @patch('requests.get')
    def test_fetch_orders_command(self, mock_get):
        # Mock the response from the requests.get call
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = self.get_xml_response()
        # mock_response._content = mock_response._content.encode('windows-1252')
        mock_get.return_value = mock_response

        # Call the management command
        call_command('fetch_orders')

        # Verify that the orders were created correctly
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.marketplace, 'amazon')
        self.assertEqual(order.order_id, '111-2222222-3333333')
        self.assertEqual(order.order_amount, Decimal('34.5'))
        self.assertEqual(order.order_tax, Decimal('0'))
        self.assertEqual(order.order_shipping, Decimal('5.5'))
        self.assertEqual(order.order_currency, 'EUR')
        self.assertEqual(order.billing_lastname, 'Tom Croisière')
        self.assertEqual(order.billing_address, '014 rue de la poupée')
        self.assertEqual(order.billing_zipcode, '75000')
        self.assertEqual(order.billing_city, 'Paris')
        self.assertEqual(order.billing_country, 'FR')
        self.assertEqual(order.billing_country_iso, 'FR')
        self.assertEqual(order.billing_phone_home, '0605050404')
        self.assertEqual(order.delivery_address, '014 rue de la poupée')
        self.assertEqual(order.delivery_zipcode, '75000')
        self.assertEqual(order.delivery_city, 'Paris')
        self.assertEqual(order.delivery_country, 'FR')
        self.assertEqual(order.delivery_country_iso, 'FR')
        self.assertEqual(order.delivery_phone_home, '0605040102')
        self.assertEqual(order.tracking_carrier, 'Standard')
        self.assertEqual(order.tracking_shipped_date, timezone.make_aware(datetime(2015, 1, 20, 16, 1, 1)))
        self.assertEqual(order.tracking_method, '')
        self.assertEqual(order.tracking_number, '')
        self.assertEqual(order.tracking_url, '')
        self.assertEqual(order.tracking_relay, '')
        self.assertEqual(order.tracking_delivering_by_marketplace, False)
        self.assertEqual(order.order_comments, '')
        self.assertEqual(order.customer_id, '')