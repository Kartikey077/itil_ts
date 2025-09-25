# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import Incident
from .serializers import IncidentSerializer

# ----------------- DRF APIs -----------------

# ✅ Login API
class LoginView(APIView):
    permission_classes = [AllowAny]  # anyone can attempt login

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)  # Django session login
            return Response({"message": "Login successful", "username": user.username})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# ✅ Logout API
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # only logged-in users can logout

    def post(self, request):
        auth_logout(request)
        return Response({"message": "Logged out"})


# ✅ Incident List & Create API
class IncidentListView(APIView):
    permission_classes = [IsAuthenticated]  # only authenticated users

    def get(self, request):
        incidents = Incident.objects.filter(created_by=request.user).order_by("-created_at")
        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IncidentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
