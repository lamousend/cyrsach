from rest_framework import serializers

from .models import Building, Equipment, Room


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