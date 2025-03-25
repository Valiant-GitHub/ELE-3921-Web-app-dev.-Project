from django.shortcuts import render
from .models import *

# Create your views here.
def home(request):
    return render(request, "home.html")


def events(request):    
    events = Events.objects.all()
    return render(request, "events.html", {"events": events})

def about(request):
    return render(request, "about.html")

def profile(request):
    return render(request, "profile.html")

def signup(request):
    return render(request, "signup.html")