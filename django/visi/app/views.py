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


def save(self, commit=True):
    instance = super().save(commit=False)
    # Debugging: Print the user and their role
    print(f"Saving availability for user: {self.user}, role: {self.user.role}")
    
    # Set the artist or venue based on the user's role
    if self.user.role == 'artist':
        instance.artist = self.user.artist_user
    elif self.user.role == 'venue':
        instance.venue = self.user.venue_user
    else:
        print("User role is not artist or venue.")
    
    if commit:
        instance.save()
    return instance



@login_required
def availability(request):
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return render(request, 'availability_success.html')  # Use the new template
    else:
        form = AvailabilityForm(user=request.user)

    return render(request, 'availability.html', {'form': form})


@login_required
def editprofile(request):
    user = request.user
    profilepic = ChangeProfilePic(instance=user)

    if user.role == "Fan":
        form = FanProfileForm
        profile = user.fan_user
    elif user.role == "Artist":
        form = ArtistProfileForm
        profile = user.artist_user
    elif user.role == "Venue":
        form = VenueProfileForm
        profile = user.venue_user
    else:
        return redirect("home")
    rolespecific = form(instance=profile)
    if request.method == "POST":
        if "profilepic" in request.POST:
            profilepic = ChangeProfilePic(request.POST, request.FILES, instance=user)
            if profilepic.is_valid():
                profilepic.save()
                return redirect("profile")
        elif "rolespecific" in request.POST:
            rolespecific = form(request.POST, request.FILES, instance=profile)
            if rolespecific.is_valid():
                rolespecific.save()
                return redirect("profile")

    return render(request, "editprofile.html", {
        "profilepic": profilepic,
        "rolespecific": rolespecific,
    })

def artistprofile(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    events = Events.objects.filter(EventArtists=artist)
    return render(request, "artistprofile.html",{"artist":artist, "events":events})

def venueprofile(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    events = Events.objects.filter(eventvenue=venue)
    photoreel = venue.user.photoreel.all()  
    return render(request, "venueprofile.html", {"venue": venue, "events": events, "photoreel": photoreel})