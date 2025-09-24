from django.urls import path
from .views import api_login, api_logout, api_incidents

urlpatterns = [
    path("api/login/", api_login, name="api_login"),
    path("api/logout/", api_logout, name="api_logout"),
    path("api/incidents/", api_incidents, name="api_incidents"),
]