from django.shortcuts import render, redirect
from .models import *
from forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
    

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
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('createprofile')  
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def createprofile(request):
    user = request.user
    if user.role == "fan":
        form_class = FanProfileForm
    elif user.role == "artist":
        form_class = ArtistProfileForm
    elif user.role == "venue":
        form_class = VenueProfileForm
    elif user.role == "doorman":
        form_class = DoormanProfileForm
    else:
        return redirect('home') 

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('home') 
    else:
        form = form_class()

    return render(request, 'profilecreation.html', {'form': form})

@login_required
def availability(request):
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, user=request.user)  # Pass the user here
        if form.is_valid():
            form.save()
            # Redirect or render a success message
    else:
        form = AvailabilityForm(user=request.user)  # Pass the user here

    return render(request, 'availability.html', {'form': form})