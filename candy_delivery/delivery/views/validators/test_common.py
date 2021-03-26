from unittest import TestCase
from candy_delivery.delivery.views.validators.common import *


class Test(TestCase):
    def test_check_id(self):
        self.assertEqual(True, check_id(1))
        self.assertEqual(False, check_id("1"))
        self.assertEqual(False, check_id(1.0))

    def test_check_id_list(self):
        self.assertEqual(True, check_id_list([1, 2, 3]))
        self.assertEqual(False, check_id_list([1.0, 2.0, 3.0]))
        self.assertEqual(False, check_id_list(["1"]))

    def test_check_hours(self):
        self.assertEqual(True, check_hours(["11:33-12:42"]))
        self.assertEqual(False, check_hours(["11:33-09:42"]))
        self.assertEqual(False, check_hours(["11:3-09:42"]))

    def test_check_courier_type(self):
        self.assertEqual(True, check_courier_type("foot"))
        self.assertEqual(True, check_courier_type("bike"))
        self.assertEqual(True, check_courier_type("car"))
        self.assertEqual(False, check_courier_type("carr"))

    def test_check_weight(self):
        self.assertEqual(True, check_weight(1))
        self.assertEqual(True, check_weight(2))
        self.assertEqual(True, check_weight(2.0))
        self.assertEqual(False, check_weight("2.0"))
        self.assertEqual(False, check_weight(111))

    def test_check_iso_datetime_string(self):
        self.assertEqual(True, check_iso_datetime_string("2021-01-10T10:33:01.42Z"))
        self.assertEqual(False, check_iso_datetime_string("2021-01-10T10:33:01.42"))
        self.assertEqual(False, check_iso_datetime_string("2021-01-10T10::01.42Z"))
        self.assertEqual(False, check_iso_datetime_string("2021-01-10T10:99:01.42Z"))
