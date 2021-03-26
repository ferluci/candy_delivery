import datetime

from candy_delivery.delivery.models import CourierTypes


def check_id(entity_id):
    return isinstance(entity_id, int) and entity_id > 0


def check_id_list(id_list):
    if not isinstance(id_list, list):
        return False

    for _id in id_list:
        if not check_id(_id):
            return False
    return True


def check_hours(hours):
    if not isinstance(hours, list):
        return False

    for hours_with_minutes in hours:
        if not check_time_string_range(hours_with_minutes):
            return False
    return True


def check_time_string_range(hours_with_minutes):
    if not isinstance(hours_with_minutes, str):
        return False

    if hours_with_minutes.find('-') == -1:
        return False

    time_start, time_end = hours_with_minutes.split('-', 1)
    dt_start = parse_hours_minutes(time_start)
    dt_end = parse_hours_minutes(time_end)
    return dt_start and dt_end and dt_end > dt_start


def parse_hours_minutes(hours_with_minutes):
    try:
        dt = datetime.datetime.strptime(hours_with_minutes, "%H:%M")
    except ValueError:
        return False
    return dt


def check_courier_type(courier_type):
    if not (isinstance(courier_type, str) and courier_type in CourierTypes.set()):
        return False
    return True


def check_weight(weight):
    return (isinstance(weight, float) or isinstance(weight, int)) and 0.01 <= weight < 50


def check_iso_datetime_string(datetime_string):
    if not isinstance(datetime_string, str):
        return False

    try:
        datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return False
    return True
