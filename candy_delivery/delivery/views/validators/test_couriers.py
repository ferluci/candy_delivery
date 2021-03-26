from unittest import TestCase

from candy_delivery.delivery.views import AddCouriersValidator, UpdateCourierValidator


class Test(TestCase):
    def test_add_couriers_validator(self):
        self.assertEqual([], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1,12,22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]))
        self.assertEqual([1], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]))
        self.assertEqual([1], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1,12,22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
                "XXX": "YYY"
            }]))
        self.assertEqual([1], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "XXX",
                "regions": [1,12,22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]))
        self.assertEqual([1], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": ["1", "12"],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]))
        self.assertEqual([1], AddCouriersValidator.validate([
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 2],
                "working_hours": ["11:95-14:05", "09:00-11:00"]
            }]))

    def test_update_courier_validator(self):
        self.assertEqual(True, UpdateCourierValidator.validate({}))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "XXX": "YYY"
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "XXX": "YYY"
        }))
        self.assertEqual(True, UpdateCourierValidator.validate({
            "regions": [1, 2]
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "regions": [2.]
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "regions": ["2"]
        }))
        self.assertEqual(True, UpdateCourierValidator.validate({
            "courier_type": "foot"
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "courier_type": "2"
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "courier_type": 1
        }))
        self.assertEqual(True, UpdateCourierValidator.validate({
            "working_hours": ["09:00-18:00"]
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "working_hours": ["09:99-18:00"]
        }))
        self.assertEqual(False, UpdateCourierValidator.validate({
            "working_hours": [0]
        }))
