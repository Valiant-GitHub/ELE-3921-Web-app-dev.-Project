from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")


def events(request):    
    return render(request, "events.html")

def about(request):
    return render(request, "about.html")

def profile(request):
    return render(request, "profile.html")

def signup(request):
    return render(request, "signup.html")