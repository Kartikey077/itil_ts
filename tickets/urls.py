from django.urls import path
from .views import raise_incident, incident_list
from .views import raise_incident, incident_list, custom_login
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('raise/', raise_incident, name='raise_incident'),
    path('', views.home, name='home'),  # root of tickets/
    path('my-incidents/', incident_list, name='incident_list'),
    path('login/', custom_login, name='login'),   # login page
    path('logout/', LogoutView.as_view(next_page='/tickets/login/'), name='logout'),
]
