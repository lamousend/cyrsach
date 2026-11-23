from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from rooms.models import Lesson, Room
from rooms.selectors import overlapping

from .models import Booking


class BookingConflict(APIException):
    status_code = 409
    default_detail = "Аудитория уже забронирована."
    default_code = "booking_conflict"


def create_booking(*, user, room_id, start, end, purpose=""):
    with transaction.atomic():
        try:
            room = Room.objects.select_for_update().get(pk=room_id, is_active=True)
        except Room.DoesNotExist:
            raise NotFound("Аудитория не найдена или закрыта для брони.")

        if overlapping(Lesson.objects.filter(room=room), start, end).exists():
            raise BookingConflict("В это время в аудитории идёт занятие.", code="lesson_conflict")

        if overlapping(Booking.objects.filter(room=room, status=Booking.Status.ACTIVE), start, end).exists():
            raise BookingConflict()

        try:
            with transaction.atomic():
                return Booking.objects.create(user=user, room=room, start=start, end=end, purpose=purpose)
        except IntegrityError:
            raise BookingConflict()


def cancel_booking(booking):
    if booking.status != Booking.Status.ACTIVE:
        raise ValidationError({"status": ["Бронь уже отменена."]})
    booking.status = Booking.Status.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])
    return booking