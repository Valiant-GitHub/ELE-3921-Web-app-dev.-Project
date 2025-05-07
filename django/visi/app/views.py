import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
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

def event(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    return render(request, "event.html", {"event": event})

@login_required
def buyticket(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    if request.method == "POST":
        if not hasattr(request.user, 'fan_user'):
            return HttpResponse("Only fans can buy tickets.")

        while True:
            ticketnumber = random.randint(10**15, 10**16 - 1)  
            if not Tickets.objects.filter(ticketnumber=ticketnumber).exists():
                break

        ticket = Tickets.objects.create(
            event=event,
            fan=request.user.fan_user,
            ticketnumber=ticketnumber
        )

        event.ticketsold += 1
        event.save()

        return redirect('ticket', ticketnumber=ticket.id)
    return HttpResponse("Theres an issue.")

def about(request):
    return render(request, "about.html")

@login_required 
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
def ticketdetails(request, ticketnumber):
    ticket = get_object_or_404(Tickets, id=ticketnumber)
    if ticket.fan.user != request.user:
        return HttpResponse("You do not have permission to view this ticket.")
    
    return render(request, "ticket.html", {"ticket": ticket})
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