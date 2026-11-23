from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Building, Equipment, Room
from .rules import validate_interval

MAX_SCHEDULE_DAYS = 31


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ("id", "name", "address")


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ("id", "name")


class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ("id", "number", "building", "capacity", "equipment", "description")


class RoomFilterSerializer(serializers.Serializer):
    building = serializers.IntegerField(required=False, min_value=1)
    min_capacity = serializers.IntegerField(required=False, min_value=1)
    equipment = serializers.CharField(required=False, allow_blank=True)

    def validate_equipment(self, value):
        if not value:
            return []
        try:
            return sorted({int(part) for part in value.split(",") if part.strip()})
        except ValueError:
            raise serializers.ValidationError("Ожидается список id через запятую, например 1,3.")



class AvailabilityQuerySerializer(RoomFilterSerializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, attrs):
        validate_interval(attrs["start"], attrs["end"], allow_past=True)
        return attrs


class ScheduleQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, attrs):
        date_from = attrs.get("date_from") or timezone.localdate()
        date_to = attrs.get("date_to") or date_from + timedelta(days=6)
        if date_to < date_from:
            raise serializers.ValidationError({"date_to": "Дата окончания раньше даты начала."})
        if (date_to - date_from).days >= MAX_SCHEDULE_DAYS:
            raise serializers.ValidationError({"date_to": f"Не больше {MAX_SCHEDULE_DAYS} дней за раз."})
        attrs["date_from"], attrs["date_to"] = date_from, date_to
        return attrs


class ScheduleItemSerializer(serializers.Serializer):
    kind = serializers.CharField()
    id = serializers.IntegerField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    title = serializers.CharField()
    lesson_type = serializers.CharField(allow_blank=True)
    is_mine = serializers.BooleanField()

class RoomShortSerializer(serializers.ModelSerializer):
    building = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Room
        fields = ("id", "number", "building")