from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Incident
import json

# ✅ API: Login
@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            password = data.get("password")
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)  # Django session cookie
            return JsonResponse({"message": "Login successful", "username": user.username})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ✅ API: Logout
@csrf_exempt
def api_logout(request):
    if request.method == "POST":
        auth_logout(request)
        return JsonResponse({"message": "Logged out"})
    return JsonResponse({"error": "Method not allowed"}, status=405)


# ✅ API: Create & List Incidents (auth required)
@csrf_exempt
def api_incidents(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    if request.method == "GET":
        incidents = Incident.objects.filter(created_by=request.user).order_by("-created_at")
        data = [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "status": i.status,
                "created_at": i.created_at.isoformat(),
            }
            for i in incidents
        ]
        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        title = payload.get("title")
        description = payload.get("description")

        if not title or not description:
            return JsonResponse({"error": "Missing fields"}, status=400)

        inc = Incident.objects.create(title=title, description=description, created_by=request.user)

        return JsonResponse({
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "status": inc.status,
            "created_at": inc.created_at.isoformat(),
        }, status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)
