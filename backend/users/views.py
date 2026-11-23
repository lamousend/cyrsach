from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, UserSerializer


class MeView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — регистрация."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []        