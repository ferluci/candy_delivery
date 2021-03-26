from candy_delivery.delivery import models
from candy_delivery.delivery.models import Courier, Region


class CouriersService:
    @staticmethod
    def add_couriers(couriers_data):
        couriers_ids = []
        for courier_data in couriers_data:
            courier = models.Courier.objects.create(
                id=courier_data['courier_id'],
                courier_type=courier_data['courier_type'],
            )
            courier.regions.set(models.Region.list_get_or_create(courier_data['regions']))
            courier.assign_working_hours(courier_data['working_hours'])
            couriers_ids.append(courier.id)
        return couriers_ids

    @classmethod
    def get_courier_stats(cls, courier_id):
        courier = Courier.objects.get(pk=courier_id)
        courier_info = cls._prepare_courier_info(courier)

        completed_orders = courier.orders.filter(courier=courier, completed=True).order_by('complete_time').all()
        if completed_orders.count() == 0:
            return courier_info

        courier_info['earnings'] = 500 * courier.earning_coefficient * completed_orders.count()
        courier_info['rating'] = courier.calculate_rating(completed_orders)
        return courier_info

    @staticmethod
    def _prepare_courier_info(courier):
        return {
            'id': courier.id,
            'courier_type': courier.courier_type,
            'regions': courier.get_regions_list(),
            'working_hours': courier.get_working_hours_list(),
            'earnings': 0
        }

    @classmethod
    def update_courier(cls, courier_id, request_body):
        # Todo: select for update
        courier = Courier.objects.get(pk=courier_id)
        is_updated = cls._update_courier_properties(courier, request_body)
        if is_updated:
            courier.save()
            for order in courier.orders.filter(completed=False).all():
                if not courier.is_order_suitable(order):
                    order.courier = None
                    order.save()
        return {
            'courier_id': courier.id,
            'courier_type': courier.courier_type,
            'regions': list(courier.regions.values_list('id', flat=True)),
            'working_hours': courier.get_working_hours_list()
        }

    @classmethod
    def _update_courier_properties(cls, courier, request_body):
        is_courier_updated = False
        if 'courier_type' in request_body and request_body['courier_type'] != courier.courier_type:
            courier.courier_type = request_body['courier_type']
            is_courier_updated = True

        if 'regions' in request_body and not courier.compare_regions(request_body['regions']):
            courier.regions.set(Region.list_get_or_create(request_body['regions']))
            is_courier_updated = True

        if 'working_hours' in request_body and not courier.compare_working_hours(request_body['working_hours']):
            courier.working_hours.all().delete()
            courier.assign_working_hours(request_body['working_hours'])
            is_courier_updated = True

        return is_courier_updated
