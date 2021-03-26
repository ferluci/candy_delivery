from candy_delivery.delivery.views.validators.common import check_hours, check_weight, check_iso_datetime_string, check_id


class AddOrdersValidator:
    add_order_fields = {'order_id', 'weight', 'region', 'delivery_hours'}

    @classmethod
    def validate(cls, orders):
        invalid_ids = []

        for order in orders:
            if not cls.check_order(order) and 'order_id' in order:
                invalid_ids.append(order['order_id'])
        return invalid_ids

    @classmethod
    def check_order(cls, order):
        if set(order.keys()) != cls.add_order_fields:
            return False

        if not check_id(order['order_id']):
            return False

        if not check_weight(order['weight']):
            return False

        if not check_id(order['region']):
            return False

        if not check_hours(order['delivery_hours']):
            return False
        return True


class AssignOrdersValidator:
    request_fields = {'courier_id'}

    @classmethod
    def validate(cls, request_body):
        if set(request_body.keys()) != cls.request_fields:
            return False

        if not check_id(request_body['courier_id']):
            return False

        return True


class CompleteOrderValidator:
    request_fields = {'courier_id', 'order_id', 'complete_time'}

    @classmethod
    def validate(cls, request_body):
        if set(request_body.keys()) != cls.request_fields:
            return False

        if not check_id(request_body['courier_id']):
            return False

        if not check_id(request_body['order_id']):
            return False

        if not check_iso_datetime_string(request_body['complete_time']):
            return False

        return True
