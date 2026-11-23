from django.contrib import admin
from django.utils import timezone

from .models import Booking


@admin.action(description="Отменить выбранные брони")
def cancel_selected(modeladmin, request, queryset):
    count = queryset.filter(status=Booking.Status.ACTIVE).update(
        status=Booking.Status.CANCELLED, cancelled_at=timezone.now()
    )
    modeladmin.message_user(request, f"Отменено броней: {count}")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "start", "end", "status", "created_at")
    list_filter = ("status", "room__building")
    search_fields = ("room__number", "user__username", "purpose")
    date_hierarchy = "start"
    autocomplete_fields = ("room", "user")
    readonly_fields = ("created_at", "cancelled_at")
    actions = [cancel_selected]