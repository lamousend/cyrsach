from rest_framework import serializers

from rooms.rules import validate_interval
from rooms.serializers import RoomShortSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    room = RoomShortSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "room", "start", "end", "purpose", "status", "created_at", "cancelled_at")
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    room = serializers.IntegerField(min_value=1)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    purpose = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        validate_interval(attrs["start"], attrs["end"])
        return attrs