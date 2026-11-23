from django.db.models import QuerySet

from .models import Lesson, Room

from bookings.models import Booking

def overlapping(qs: QuerySet, start, end) -> QuerySet:
    return qs.filter(start__lt=end, end__gt=start)


def filter_rooms(qs: QuerySet, *, building=None, min_capacity=None, equipment=()) -> QuerySet:
    if building:
        qs = qs.filter(building_id=building)
    if min_capacity:
        qs = qs.filter(capacity__gte=min_capacity)
    for equipment_id in equipment:
        qs = qs.filter(equipment__id=equipment_id)
    return qs


def available_rooms(start, end, **filters) -> QuerySet:
    busy_by_lessons = overlapping(Lesson.objects.all(), start, end).values("room_id")
    busy_by_bookings = overlapping(
        Booking.objects.filter(status=Booking.Status.ACTIVE), start, end
    ).values("room_id")

    qs = Room.objects.filter(is_active=True).select_related("building").prefetch_related("equipment")
    qs = filter_rooms(qs, **filters)
    qs = qs.exclude(id__in=busy_by_lessons).exclude(id__in=busy_by_bookings)
    return qs.order_by("capacity", "building__name", "number")