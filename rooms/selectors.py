from django.db.models import QuerySet


def filter_rooms(qs: QuerySet, *, building=None, min_capacity=None, equipment=()) -> QuerySet:
    if building:
        qs = qs.filter(building_id=building)
    if min_capacity:
        qs = qs.filter(capacity__gte=min_capacity)
    for equipment_id in equipment:
        qs = qs.filter(equipment__id=equipment_id)
    return qs