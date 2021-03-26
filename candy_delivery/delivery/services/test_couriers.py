from django.db import IntegrityError
from django.test import TestCase

from candy_delivery.delivery.models import Region, WorkingHoursRange, Order, Courier
from candy_delivery.delivery.services import CouriersService


class TestAddCouriers(TestCase):
    def test_add_couriers(self) -> None:
        couriers_data = [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            }
        ]
        added_couriers = CouriersService.add_couriers(couriers_data)
        self.assertEqual([1, 2, 3], added_couriers)

        regions = Region.objects.all()
        self.assertEqual({1, 12, 22, 23, 33}, {region.id for region in regions})

        self.assertEqual(
            {"11:35-14:05", "09:00-11:00"},
            {str(x) for x in WorkingHoursRange.objects.filter(courier_id=1).all()}
        )
        self.assertEqual(
            {"09:00-18:00"},
            {str(x) for x in WorkingHoursRange.objects.filter(courier_id=2).all()}
        )
        self.assertEqual(
            set(),
            {str(x) for x in WorkingHoursRange.objects.filter(courier_id=3).all()}
        )

        # Check duplication adding
        with self.assertRaises(IntegrityError):
            CouriersService.add_couriers(couriers_data)


class TestGetCourierStats(TestCase):
    def setUp(self) -> None:
        CouriersService.add_couriers([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 2, 3],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }])

        CouriersService.add_couriers([
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [1, 2, 3],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }])

    def test_get_courier_stats(self):
        self.assertEqual({
            'id': 1,
            'courier_type': 'foot',
            'regions': [1, 2, 3],
            'working_hours': ['11:35-14:05', '09:00-11:00'],
            'earnings': 0
        }, CouriersService.get_courier_stats(1))

        first_region, _ = Region.objects.get_or_create(id=1)
        Order.objects.create(
            id=1, courier_id=1, weight=1, region=first_region,
            completed=True, complete_time="2021-03-24 14:00:00",)
        Order.objects.filter(id=1).update(assign_time="2021-03-24 12:00:00")

        Order.objects.create(
            id=2, courier_id=1, weight=1, region=first_region,
            completed=True, complete_time="2021-03-24 14:05:00")
        Order.objects.filter(id=2).update(assign_time="2021-03-24 08:05:00")

        first_region_average_time = (2 * 3600 + 5 * 60) / 2
        self.assertEqual({
            'id': 1,
            'courier_type': 'foot',
            'regions': [1, 2, 3],
            'working_hours': ['11:35-14:05', '09:00-11:00'],
            'earnings': 2 * 500 * 2,
            'rating': 0.0,
        }, CouriersService.get_courier_stats(1))

        second_region, _ = Region.objects.get_or_create(id=2)
        Order.objects.create(
            id=3, courier_id=1, weight=1, region=second_region,
            completed=True, complete_time="2021-03-24 08:55:00",)
        Order.objects.filter(id=3).update(assign_time="2021-03-24 08:35:00")

        Order.objects.create(
            id=4, courier_id=1, weight=1, region=second_region,
            completed=True, complete_time="2021-03-24 08:15:00")
        Order.objects.filter(id=4).update(assign_time="2021-03-24 08:05:00")

        second_region_average_time = (40 * 60 + 10 * 60) / 2
        self.assertEqual({
            'id': 1,
            'courier_type': 'foot',
            'regions': [1, 2, 3],
            'working_hours': ['11:35-14:05', '09:00-11:00'],
            'earnings': 2 * 500 * 4,
            'rating': (60 * 60 - min(first_region_average_time, second_region_average_time)) / (60 * 60) * 5,
        }, CouriersService.get_courier_stats(1))

        third_region, _ = Region.objects.get_or_create(id=3)

        Order.objects.create(
            id=5, courier_id=1, weight=1, region=third_region,
            completed=True, complete_time="2021-03-24 08:15:00")
        Order.objects.filter(id=5).update(assign_time="2021-03-24 08:05:00")

        Order.objects.create(
            id=6, courier_id=1, weight=1, region=third_region,
            completed=True, complete_time="2021-03-24 08:20:00",)
        Order.objects.filter(id=6).update(assign_time="2021-03-24 08:05:00")

        Order.objects.create(
            id=7, courier_id=1, weight=1, region=third_region,
            completed=True, complete_time="2021-03-24 08:45:00")
        Order.objects.filter(id=7).update(assign_time="2021-03-24 08:05:00")

        third_region_average_time = (10 * 60 + 5 * 60 + 25 * 60) / 3

        minimal_delivery_time = min([first_region_average_time, second_region_average_time, third_region_average_time])
        self.assertEqual({
            'id': 1,
            'courier_type': 'foot',
            'regions': [1, 2, 3],
            'working_hours': ['11:35-14:05', '09:00-11:00'],
            'earnings': 2 * 500 * 7,
            'rating': (60 * 60 - minimal_delivery_time) / (60 * 60) * 5,
        }, CouriersService.get_courier_stats(1))

        Order.objects.create(
            id=8, courier_id=2, weight=1, region=first_region,
            completed=True, complete_time="2021-03-24 14:00:00",)
        Order.objects.filter(id=8).update(assign_time="2021-03-24 12:00:00")

        Order.objects.create(
            id=9, courier_id=2, weight=1, region=first_region,
            completed=True, complete_time="2021-03-24 14:05:00")
        Order.objects.filter(id=9).update(assign_time="2021-03-24 08:05:00")

        self.assertEqual({
            'id': 2,
            'courier_type': 'bike',
            'regions': [1, 2, 3],
            'working_hours': ['11:35-14:05', '09:00-11:00'],
            'earnings': 5 * 500 * 2,
            'rating': 0.0,
        }, CouriersService.get_courier_stats(2))


class TestGetCourierUpdate(TestCase):
    def setUp(self) -> None:
        CouriersService.add_couriers([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 2, 3],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }])

    def test_update_courier(self):
        self.assertEqual({
            "courier_id": 1,
            "courier_type": "bike",
            "regions": [1, 2, 3],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }, CouriersService.update_courier(1, {'courier_type': 'bike'}))

        self.assertEqual({
            "courier_id": 1,
            "courier_type": "bike",
            "regions": [1, 2],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }, CouriersService.update_courier(1, {'regions': [1, 2]}))

        self.assertEqual({
            "courier_id": 1,
            "courier_type": "bike",
            "regions": [1, 2],
            "working_hours": ["11:35-14:05"]
        }, CouriersService.update_courier(1, {'working_hours': ["11:35-14:05"]}))

        self.assertEqual(1, WorkingHoursRange.objects.count())

        first_region, _ = Region.objects.get_or_create(id=1)
        Order.objects.create(
            id=1, courier_id=1, weight=12, region=first_region,
            completed=False)
        Order.objects.filter(id=1).update(assign_time="2021-03-24 12:00:00")

        courier = Courier.objects.get(pk=1)
        self.assertEqual(1, courier.orders.count())

        self.assertEqual({
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 2],
            "working_hours": ["11:35-14:05"]
        }, CouriersService.update_courier(1, {'courier_type': 'foot'}))

        courier = Courier.objects.get(pk=1)
        self.assertEqual(0, courier.orders.count())
        self.assertEqual(1, Order.objects.count())
        order = Order.objects.get(pk=1)
        self.assertEqual(False, order.completed)
