from unittest import TestCase

from candy_delivery.delivery.views import AddOrdersValidator, AssignOrdersValidator, CompleteOrderValidator


class Test(TestCase):
    def test_add_orders_validator(self):
        self.assertEqual([], AddOrdersValidator.validate([]))
        self.assertEqual([1], AddOrdersValidator.validate([
            {
                'order_id': 1,
            },
        ]))

        self.assertEqual([1, 3, 4, 5, 6, 7, 8], AddOrdersValidator.validate([
            {
                'order_id': 1,
            },
            {
                'order_id': 2,
                'weight': 5,
                'region': 1,
                'delivery_hours': ["09:00-11:00"]
            },
            {
                'order_id': 3,
                'weight': 55,
                'region': 1,
                'delivery_hours': ["09:00-11:00"]
            },
            {
                'order_id': 4,
                'weight': "55",
                'region': 1,
                'delivery_hours': ["09:00-11:00"]
            },
            {
                'order_id': 5,
                'weight': 1,
                'region': "1",
                'delivery_hours': ["09:00-11:00"]
            },
            {
                'order_id': 6,
                'weight': 1,
                'region': [1],
                'delivery_hours': ["09:00-11:00"]
            },
            {
                'order_id': 7,
                'weight': 1,
                'region': 1,
                'delivery_hours': ["09:99-11:00"]
            },
            {
                'order_id': 8,
                'weight': 1,
                'region': 1,
                'delivery_hours': ["09:99-11:00"],
                "XXX": "YYY"
            }
        ]))

    def test_assign_orders_validator(self):
        self.assertEqual(False, AssignOrdersValidator.validate({}))
        self.assertEqual(True, AssignOrdersValidator.validate({
            "courier_id": 2
        }))
        self.assertEqual(False, AssignOrdersValidator.validate({
            "courier_id": 0
        }))
        self.assertEqual(False, AssignOrdersValidator.validate({
            "courier_id": "1"
        }))
        self.assertEqual(False, AssignOrdersValidator.validate({
            "courier_id": "1",
            "XXX": "YYY"
        }))

    def test_complete_order_validator(self):
        self.assertEqual(True, CompleteOrderValidator.validate({
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }))
        self.assertEqual(False, CompleteOrderValidator.validate({
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }))
        self.assertEqual(False, CompleteOrderValidator.validate({
            "courier_id": "1",
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }))
        self.assertEqual(False, CompleteOrderValidator.validate({
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z",
            "XXX": "YYYY"
        }))
        self.assertEqual(False, CompleteOrderValidator.validate({
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:99:01.42Z"
        }))
        self.assertEqual(False, CompleteOrderValidator.validate({
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42ZA"
        }))
