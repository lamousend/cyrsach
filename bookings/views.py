from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer
from .services import cancel_booking, create_booking


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = BookingCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)           
        v = data.validated_data
        booking = create_booking(                      
            user=request.user, room_id=v["room"], start=v["start"], end=v["end"], purpose=v["purpose"]
        )
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.filter(user=self.request.user).select_related("room__building")
        status_filter = self.request.query_params.get("status")
        if status_filter in Booking.Status.values:
            qs = qs.filter(status=status_filter)
        return qs


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking.objects.select_related("room__building"), pk=pk)
        if booking.user_id != request.user.id and not request.user.is_room_admin:
            raise PermissionDenied("Можно отменить только свою бронь.")   
        cancel_booking(booking)
        return Response(BookingSerializer(booking).data)