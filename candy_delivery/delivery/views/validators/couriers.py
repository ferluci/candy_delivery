from candy_delivery.delivery.views.validators.common import *


class AddCouriersValidator:
    add_courier_fields = {'courier_id', 'courier_type', 'regions', 'working_hours'}

    @classmethod
    def validate(cls, couriers):
        invalid_ids = []

        for courier in couriers:
            if not cls._check_courier(courier) and 'courier_id' in courier:
                invalid_ids.append(courier['courier_id'])
        return invalid_ids

    @classmethod
    def _check_courier(cls, courier):
        if set(courier.keys()) != cls.add_courier_fields:
            return False

        if not check_id(courier['courier_id']):
            return False

        if not check_courier_type(courier['courier_type']):
            return False

        if not check_id_list(courier['regions']):
            return False

        if not check_hours(courier['working_hours']):
            return False
        return True


class UpdateCourierValidator:
    update_courier_fields = {'courier_type', 'regions', 'working_hours'}

    @classmethod
    def validate(cls, courier_req):
        if not set(courier_req.keys()).issubset(cls.update_courier_fields):
            return False

        if 'courier_type' in courier_req and not check_courier_type(courier_req['courier_type']):
            return False

        if 'regions' in courier_req and not check_id_list(courier_req['regions']):
            return False

        if 'working_hours' in courier_req and not check_hours(courier_req['working_hours']):
            return False

        return True
