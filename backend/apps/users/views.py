from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.serializers import LimpTokenObtainPairSerializer, UserMeSerializer


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST"), name="dispatch")
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    serializer_class = LimpTokenObtainPairSerializer


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes: list = []


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Client discards tokens; refresh blacklist can be added later.
        return Response({"detail": "logged_out"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)
