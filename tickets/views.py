from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Incident
from django.http import HttpResponse

# Page to raise a new ticket
@login_required
def raise_incident(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        Incident.objects.create(title=title, description=description, created_by=request.user)
        return redirect('incident_list')
    return render(request, 'tickets/raise_incident.html')

# Page to list all tickets of the logged-in user
@login_required
def incident_list(request):
    incidents = Incident.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'tickets/incident_list.html', {'incidents': incidents})

# Custom login page
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('incident_list')
        else:
            return render(request, 'tickets/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tickets/login.html')

def home(request):
    return HttpResponse("<h1>Welcome to ITIL Ticketing System</h1>")