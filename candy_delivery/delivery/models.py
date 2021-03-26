import datetime

from django.db import models


class Region(models.Model):
    @classmethod
    def list_get_or_create(cls, ids):
        regions_exist_ids = cls.objects.filter(id__in=ids).order_by('id').values_list('id', flat=True)

        not_existed_regions = [id for id in ids if id not in regions_exist_ids]
        if len(not_existed_regions) > 0:
            cls.objects.bulk_create([cls(id=id) for id in not_existed_regions])

        return cls.objects.filter(id__in=ids)

    class Meta:
        db_table = 'region'


class TimeRange(models.Model):
    start_hours = models.IntegerField()
    start_minutes = models.IntegerField()

    end_hours = models.IntegerField()
    end_minutes = models.IntegerField()

    def __str__(self):
        return "{:02d}:{:02d}-{:02d}:{:02d}".format(
            self.start_hours, self.start_minutes, self.end_hours, self.end_minutes,
        )

    def is_intersect(self, time_range):
        # x0 < y1 and x1 > y0
        return (
                self.start_minutes <= time_range.end_minutes and
                self.start_hours <= time_range.end_hours and
                self.end_minutes >= time_range.start_minutes and
                self.end_hours >= time_range.start_hours
        )

    class Meta:
        abstract = True


class CourierTypes:
    FOOT = 'foot'
    BIKE = 'bike'
    CAR = 'car'

    _EARNING_COEFFICIENTS = {
        FOOT: 2,
        BIKE: 5,
        CAR: 9,
    }

    _CAPACITIES = {
        FOOT: 10,
        BIKE: 15,
        CAR: 50,
    }

    CHOICES = (
        (FOOT, FOOT),
        (BIKE, BIKE),
        (CAR, CAR)
    )

    @classmethod
    def set(cls):
        return {cls.FOOT, cls.CAR, cls.BIKE}

    @classmethod
    def earning_coefficient(cls, courier_type):
        return cls._EARNING_COEFFICIENTS.get(courier_type, 0)

    @classmethod
    def get_capacity(cls, courier_type):
        return cls._CAPACITIES.get(courier_type, 0)


class Courier(models.Model):
    courier_type = models.TextField(choices=CourierTypes.CHOICES, default=CourierTypes.FOOT)
    regions = models.ManyToManyField(Region, db_table='courier_region')

    _capacity = 0

    def __init__(self, *args, **kwargs):
        super(Courier, self).__init__(*args, **kwargs)
        self._capacity = CourierTypes.get_capacity(self.courier_type)

    @property
    def earning_coefficient(self):
        return CourierTypes.earning_coefficient(self.courier_type)

    @property
    def capacity(self):
        return self._capacity

    def calculate_rating(self, completed_orders):
        completed_orders = completed_orders.order_by('region_id', 'complete_time')
        regions_delivery_times = {}
        for i in range(len(completed_orders)):
            if completed_orders[i].region_id not in regions_delivery_times:
                time_diff = completed_orders[i].complete_time - completed_orders[i].assign_time
                delivery_time = time_diff.total_seconds()
            else:
                time_diff = completed_orders[i].complete_time - completed_orders[i-1].complete_time
                delivery_time = time_diff.total_seconds()
            order_region = completed_orders[i].region_id
            region_delivery_times = regions_delivery_times.get(order_region, [])
            region_delivery_times.append(delivery_time)
            regions_delivery_times[order_region] = region_delivery_times
        min_region_delivery_time = min([sum(x)/len(x) for x in regions_delivery_times.values()])
        rating = (60*60 - min(min_region_delivery_time, 60*60))/(60*60) * 5
        return rating

    def get_working_hours_list(self):
        return [str(x) for x in self.working_hours.all()]

    def get_regions_list(self):
        return [region.id for region in self.regions.all()]

    def assign_working_hours(self, hours_list):
        courier_working_hours = []
        for time_range in hours_list:
            time_start, time_end = time_range.split('-', 1)
            time_start = datetime.datetime.strptime(time_start, "%H:%M")
            time_end = datetime.datetime.strptime(time_end, "%H:%M")
            working_hours_range = WorkingHoursRange(
                start_hours=time_start.hour,
                start_minutes=time_start.minute,
                end_hours=time_end.hour,
                end_minutes=time_end.minute,
                courier=self,
            )
            courier_working_hours.append(working_hours_range)
        WorkingHoursRange.objects.bulk_create(courier_working_hours)

    def compare_regions(self, regions):
        return set(regions) == set(self.regions.values_list('id', flat=True))

    def compare_working_hours(self, working_hours):
        return set(working_hours) == set(self.get_working_hours_list())

    def is_order_suitable(self, order):
        if order.weight > self.capacity:
            return False

        if order.region not in self.regions.all():
            return False

        for delivery_shift in order.delivery_hours.all():
            for working_shift in self.working_hours.all():
                if delivery_shift.is_intersect(working_shift):
                    return True
        return False

    class Meta:
        db_table = 'courier'


class WorkingHoursRange(TimeRange):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='working_hours')

    class Meta:
        db_table = 'courier_working_hours'


class Order(models.Model):
    weight = models.FloatField()
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, related_name='orders', null=True)
    assign_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    complete_time = models.DateTimeField(null=True)

    def assign_delivery_hours(self, hours_list):
        order_delivery_hours = []
        for time_range in hours_list:
            time_start, time_end = time_range.split('-', 1)
            time_start = datetime.datetime.strptime(time_start, "%H:%M")
            time_end = datetime.datetime.strptime(time_end, "%H:%M")
            delivery_hours_range = DeliveryHours(
                start_hours=time_start.hour,
                start_minutes=time_start.minute,
                end_hours=time_end.hour,
                end_minutes=time_end.minute,
                order=self,
            )
            order_delivery_hours.append(delivery_hours_range)
        DeliveryHours.objects.bulk_create(order_delivery_hours)

    def complete(self, complete_time):
        self.completed = True
        self.complete_time = complete_time
        self.save()

    class Meta:
        db_table = 'order'


class DeliveryHours(TimeRange):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_hours')

    class Meta:
        db_table = 'order_delivery_hours'
