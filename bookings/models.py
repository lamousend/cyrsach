from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.db import models
from django.db.models import F, Func, Q


class TsTzRange(Func):
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class Booking(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELLED = "cancelled", "Отменена"

    room = models.ForeignKey(
        "rooms.Room", on_delete=models.PROTECT, related_name="bookings", verbose_name="аудитория"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings", verbose_name="пользователь"
    )
    start = models.DateTimeField("начало")
    end = models.DateTimeField("конец")
    purpose = models.CharField("цель", max_length=255, blank=True)
    status = models.CharField("статус", max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField("создана", auto_now_add=True)   # заполняется само
    cancelled_at = models.DateTimeField("отменена", null=True, blank=True)

    class Meta:
        db_table = "bookings"
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"
        ordering = ["-start"]
        constraints = [
            models.CheckConstraint(condition=Q(start__lt=F("end")), name="booking_start_before_end"),
            ExclusionConstraint(
                name="exclude_overlapping_active_bookings",
                expressions=[
                    (TsTzRange("start", "end", RangeBoundary()), RangeOperators.OVERLAPS),  
                    ("room", RangeOperators.EQUAL),                                         
                ],
                condition=Q(status="active"),
            ),
        ]

    def __str__(self):
        return f"{self.room} {self.start:%d.%m %H:%M}–{self.end:%H:%M}"