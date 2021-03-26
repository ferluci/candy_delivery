import json
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

from candy_delivery.delivery.models import Order
from candy_delivery.delivery.services import OrdersService
from candy_delivery.delivery.views.validators import AddOrdersValidator
from candy_delivery.delivery.views.validators.orders import AssignOrdersValidator, CompleteOrderValidator


def add_orders(request):
    try:
        request_body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid json')

    if not request_body['data']:
        return HttpResponseBadRequest('No data property in request body')

    invalid_ids = AddOrdersValidator.validate(request_body['data'])
    if len(invalid_ids) != 0:
        return HttpResponseBadRequest(json.dumps({
            "validation_error": {
                "orders": [{'id': x} for x in invalid_ids]
            }
        }))

    try:
        orders_ids = OrdersService.add_orders(request_body['data'])
        return HttpResponse(json.dumps({
            "couriers": {
                "orders": [{'id': x} for x in orders_ids]
            }
        }), status=201)
    except IntegrityError:
        return HttpResponseBadRequest('Duplication id error')


def assign_orders(request):
    try:
        request_body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid json')

    if not AssignOrdersValidator.validate(request_body):
        return HttpResponseBadRequest('Invalid request body')

    assign_time = datetime.datetime.now()
    try:
        assigned_orders = OrdersService.assign_orders(
            request_body['courier_id'],
            assign_time
        )
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Courier not found')

    response = {
        "orders": [{"id": x} for x in assigned_orders]
    }
    if len(assigned_orders) > 0:
        response['assign_time'] = assign_time.isoformat()

    return JsonResponse(response)


def complete_order(request):
    try:
        request_body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid json')

    if not CompleteOrderValidator.validate(request_body):
        return HttpResponseBadRequest('Invalid request body')

    try:
        order = Order.objects.get(pk=request_body['order_id'], courier_id=request_body['courier_id'])
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('Can\'t find an order for such request')

    order.complete(request_body['complete_time'])

    return JsonResponse({
        "order_id": order.id,
    })
