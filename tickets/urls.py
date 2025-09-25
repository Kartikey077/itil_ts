from django.urls import path
from .views import LoginView, LogoutView, IncidentListView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('incidents/', IncidentListView.as_view(), name='incidents'),
]
