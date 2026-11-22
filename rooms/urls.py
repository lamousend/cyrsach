from django.urls import path

from . import views

urlpatterns = [
    path("buildings/", views.BuildingListView.as_view()),
    path("equipment/", views.EquipmentListView.as_view()),
    path("rooms/", views.RoomListView.as_view()),
    path("rooms/<int:pk>/", views.RoomDetailView.as_view()),
]