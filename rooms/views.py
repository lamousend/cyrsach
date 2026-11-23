from datetime import datetime, time, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Building, Equipment, Room
from .selectors import available_rooms, filter_rooms, overlapping
from .serializers import AvailabilityQuerySerializer, BuildingSerializer, EquipmentSerializer, RoomFilterSerializer, RoomSerializer, ScheduleItemSerializer, ScheduleQuerySerializer

from bookings.models import Booking

AVAILABILITY_NOTE = (
    "Свободна по доступному расписанию: в базе есть не все группы, "
    "поэтому занятость может быть неполной."
)


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
        qs = Room.objects.filter(is_active=True).select_related("building").prefetch_related("equipment")
        return filter_rooms(qs, **params.validated_data)


class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.select_related("building").prefetch_related("equipment")
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
class RoomAvailableView(APIView):
    """GET /api/rooms/available/?start=...&end=...&building=&min_capacity=&equipment="""

    permission_classes = [AllowAny]

    def get(self, request):
        params = AvailabilityQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        data = dict(params.validated_data)
        start, end = data.pop("start"), data.pop("end")   
        rooms = available_rooms(start, end, **data)
        return Response(
            {
                "start": timezone.localtime(start),
                "end": timezone.localtime(end),
                "availability_note": AVAILABILITY_NOTE,
                "count": len(rooms),
                "results": RoomSerializer(rooms, many=True).data,
            }
        )


class RoomScheduleView(APIView):
    """GET /api/rooms/5/schedule/?date_from=2026-11-24&date_to=2026-11-30"""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        room = get_object_or_404(Room.objects.select_related("building"), pk=pk)
        params = ScheduleQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        date_from = params.validated_data["date_from"]
        date_to = params.validated_data["date_to"]

        range_start = timezone.make_aware(datetime.combine(date_from, time.min))
        range_end = timezone.make_aware(datetime.combine(date_to + timedelta(days=1), time.min))

        items = [
            {
                "kind": "lesson",
                "id": lesson.id,
                "start": lesson.start,
                "end": lesson.end,
                "title": lesson.subject,
                "lesson_type": lesson.lesson_type,
                "is_mine": False,
            }
            for lesson in overlapping(room.lessons.all(), range_start, range_end)
        ]
        user = request.user
        items += [
            {
                "kind": "booking",
                "id": booking.id,
                "start": booking.start,
                "end": booking.end,
                "title": "Забронировано",  
                "lesson_type": "",
                "is_mine": user.is_authenticated and booking.user_id == user.id,
            }
            for booking in overlapping(
                room.bookings.filter(status=Booking.Status.ACTIVE), range_start, range_end
            )
        ]
    
        items.sort(key=lambda item: item["start"])

        return Response(
            {
                "room": RoomSerializer(room).data,
                "date_from": date_from,
                "date_to": date_to,
                "availability_note": AVAILABILITY_NOTE,
                "items": ScheduleItemSerializer(items, many=True).data,
            }
        )