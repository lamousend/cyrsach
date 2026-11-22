from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Building, Equipment, Room
from .selectors import filter_rooms
from .serializers import BuildingSerializer, EquipmentSerializer, RoomFilterSerializer, RoomSerializer


class BuildingListView(generics.ListAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [AllowAny]     


class EquipmentListView(generics.ListAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]


class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        params = RoomFilterSerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        qs = (
            Room.objects.filter(is_active=True)
            .select_related("building")  
            .prefetch_related("equipment")
        )
        return filter_rooms(qs, **params.validated_data)


class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.select_related("building").prefetch_related("equipment")
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]