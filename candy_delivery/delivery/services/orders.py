from django.db.models import Q
from candy_delivery.delivery.models import Order, Courier, Region


class OrdersService:
    @staticmethod
    def add_orders(orders_data):
        orders_ids = []
        for order_data in orders_data:
            order = Order.objects.create(
                id=order_data['order_id'],
                weight=order_data['weight']
            )
            order.region, _ = Region.objects.get_or_create(id=order_data['region'])
            order.assign_delivery_hours(order_data['delivery_hours'])
            order.save()
            orders_ids.append(order.id)
        return orders_ids

    @classmethod
    def assign_orders(cls, courier_id, assign_time):
        courier = Courier.objects.get(pk=courier_id)
        # Todo: select for update
        assigned_orders = []
        for order in cls._get_potential_orders(courier).all():
            if courier.is_order_suitable(order):
                order.courier = courier
                order.assign_time = assign_time
                order.save()
                assigned_orders.append(order.id)
        return assigned_orders

    @classmethod
    def _get_potential_orders(cls, courier):
        delivery_hours_filter = None
        for work_shift in courier.working_hours.all():
            shift_filter = Order.objects.filter(
                Q(delivery_hours__start_hours__lte=work_shift.end_hours) &
                Q(delivery_hours__start_minutes__lte=work_shift.end_minutes) &
                Q(delivery_hours__end_hours__gte=work_shift.start_hours) &
                Q(delivery_hours__end_minutes__gte=work_shift.start_minutes)
            )
            if delivery_hours_filter is not None:
                delivery_hours_filter = delivery_hours_filter | shift_filter
            else:
                delivery_hours_filter = shift_filter

        return delivery_hours_filter & Order.objects.filter(
            Q(courier__isnull=True) & Q(region__in=courier.get_regions_list())
        )
