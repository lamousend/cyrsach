from django.urls import path

from . import views

urlpatterns = [
    path("", views.BookingCreateView.as_view()),
    path("my/", views.MyBookingsView.as_view()),
    path("<int:pk>/cancel/", views.BookingCancelView.as_view()),
]