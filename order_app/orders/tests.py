from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from orders.utils import safe_datetime_conversion, safe_decimal_conversion

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