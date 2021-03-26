import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views import View

from candy_delivery.delivery.services import CouriersService
from candy_delivery.delivery.views.validators.couriers import UpdateCourierValidator
from .validators import AddCouriersValidator


def add_couriers(request):
    try:
        request_body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid json')

    if not request_body['data']:
        return HttpResponseBadRequest('No data property in request body')

    invalid_ids = AddCouriersValidator.validate(request_body['data'])
    if len(invalid_ids) != 0:
        return HttpResponse(json.dumps({
            "validation_error": {
                "couriers": [{'id': x} for x in invalid_ids]
            }
        }), status=400)

    try:
        couriers_ids = CouriersService.add_couriers(request_body['data'])
    except IntegrityError:
        return HttpResponseBadRequest('Duplication id error')

    return HttpResponse(json.dumps({
        "couriers": {
            "couriers": [{'id': x} for x in couriers_ids]
        }
    }), status=201)


class CouriersView(View):
    # get courier information
    def get(self, request, courier_id):
        try:
            courier_stats = CouriersService.get_courier_stats(courier_id)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Courier not found')
        return JsonResponse(courier_stats)

    # update courier properties
    def patch(self, request, courier_id):
        try:
            request_body = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid request body')

        if not UpdateCourierValidator.validate(request_body):
            return HttpResponseBadRequest('Invalid request')

        try:
            courier_info = CouriersService.update_courier(courier_id, request_body)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Courier not found')

        return JsonResponse(courier_info)
