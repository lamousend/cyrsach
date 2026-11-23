from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def validate_interval(start, end, *, allow_past=False):
    day_start = settings.BOOKING_DAY_START
    day_end = settings.BOOKING_DAY_END

    if start >= end:
        raise ValidationError({"end": ["Окончание должно быть позже начала."]})

    
    local_start, local_end = timezone.localtime(start), timezone.localtime(end)
    if local_start.date() != local_end.date():
        raise ValidationError({"end": ["Интервал должен укладываться в один день."]})
    if local_start.time() < day_start or local_end.time() > day_end:
        raise ValidationError(
            {"non_field_errors": [f"Бронировать можно с {day_start:%H:%M} до {day_end:%H:%M}."]}
        )

    duration = end - start
    if duration < settings.BOOKING_MIN_DURATION:
        raise ValidationError({"end": ["Слишком короткий интервал (минимум 15 минут)."]})
    if duration > settings.BOOKING_MAX_DURATION:
        raise ValidationError({"end": ["Слишком длинный интервал (максимум 4 часа)."]})

    if not allow_past and start < timezone.now():
        raise ValidationError({"start": ["Нельзя бронировать прошедшее время."]})