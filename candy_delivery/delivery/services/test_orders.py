import datetime

import pytz

from django.test import TestCase

from candy_delivery.delivery.models import Order, DeliveryHours, Region, Courier
from candy_delivery.delivery.services import OrdersService, CouriersService


class TestAddOrders(TestCase):
    def test_add_orders(self):
        OrdersService.add_orders([
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            }])
        self.assertEqual(2, Order.objects.count())
        self.assertEqual(2, DeliveryHours.objects.count())
        self.assertEqual(2, Region.objects.count())


class TestAssignOrders(TestCase):
    def setUp(self) -> None:
        CouriersService.add_couriers([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 2, 3],
                "working_hours": ["11:00-14:00", "19:00-21:00"]
            }])

        OrdersService.add_orders([
            # Yes
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            # No
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            # Yes
            {
                "order_id": 3,
                "weight": 10,
                "region": 1,
                "delivery_hours": ["20:00-22:00"]
            },
            # No
            {
                "order_id": 4,
                "weight": 1,
                "region": 10,
                "delivery_hours": ["00:00-23:00"]
            },
            # Yes
            {
                "order_id": 5,
                "weight": 1,
                "region": 1,
                "delivery_hours": ["09:00-12:00"]
            },
            # Yes
            {
                "order_id": 6,
                "weight": 1,
                "region": 1,
                "delivery_hours": ["13:00-15:00"]
            },
            # No
            {
                "order_id": 7,
                "weight": 1,
                "region": 1,
                "delivery_hours": ["15:00-17:00"]
            },
            # Yes
            {
                "order_id": 8,
                "weight": 1,
                "region": 1,
                "delivery_hours": ["00:00-23:00"]
            },
        ])

    def test_assign_orders(self):
        assign_time = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.UTC)
        assigned_orders = OrdersService.assign_orders(1, assign_time)
        self.assertEqual([1, 3, 5, 6, 8], assigned_orders)

        courier_orders = Courier.objects.get(pk=1).orders.all()
        for order in courier_orders:
            self.assertEqual(assign_time, order.assign_time)
