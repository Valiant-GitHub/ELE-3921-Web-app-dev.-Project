import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .utils import role_required


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
@role_required(['artist', 'venue'])
def availability(request):
    if request.method == 'POST':
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('availabilitysuccess')  # Redirect to a success page
    else:
        form = AvailabilityForm(user=request.user)

    return render(request, 'availabilityform.html', {'form': form})

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


@login_required
@role_required(['artist', 'venue'])
def availability_success(request):
    return render(request, 'availabilitysuccess.html')

def artistprofile(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    events = Events.objects.filter(EventArtists=artist)
    return render(request, "artistprofile.html",{"artist":artist, "events":events})

def venueprofile(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    events = Events.objects.filter(eventvenue=venue)
    photoreel = venue.user.photoreel.all()  
    return render(request, "venueprofile.html", {"venue": venue, "events": events, "photoreel": photoreel})

@login_required
@role_required(['artist', 'venue'])
def available(request):
    availabilities = Availability.objects.all().order_by('start_time')
    return render(request, 'available.html', {'availabilities': availabilities})

@login_required
@role_required(['artist', 'venue'])
def requestbooking(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.availability = availability
            booking.save()
            return redirect('bookingsuccess')  # Redirect to a success page
    else:
        form = BookingForm()
    return render(request, 'booking.html', {'form': form, 'availability': availability})

@login_required
@role_required(['artist', 'venue'])
def bookingsuccess(request):
    return render(request, 'bookingsuccess.html')

@login_required
@role_required(['artist', 'venue'])
def dashboard(request):
    # Get the logged-in user's availability slots
    if request.user.role == 'artist':
        availabilities = Availability.objects.filter(artist__user=request.user)
    elif request.user.role == 'venue':
        availabilities = Availability.objects.filter(venue__user=request.user)
    else:
        availabilities = Availability.objects.none()

    # Get all bookings for those availability slots
    bookings = Booking.objects.filter(availability__in=availabilities)

    # Prepare data for the calendar
    calendar_events = []
    for booking in bookings:
        color = (
            'green' if booking.status == 'approved' else
            'orange' if booking.status == 'pending' else
            'red'
        )
        calendar_events.append({
            'title': booking.availability.description,
            'start': booking.availability.start_time.isoformat(),
            'end': booking.availability.end_time.isoformat(),
            'color': color,
        })

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        booking = get_object_or_404(Booking, id=booking_id)

        if action == 'approve':
            booking.status = 'approved'
        elif action == 'reject':
            booking.status = 'rejected'
        booking.save()

        return redirect('dashboard')  # Redirect back to the dashboard

    return render(request, 'dashboard.html', {
        'availabilities': availabilities,
        'bookings': bookings,
        'calendar_events': calendar_events,  # Pass calendar data to the template
    })


@login_required
@role_required(['artist', 'venue'])
def listingdetail(request, listing_id, listing_type):
    """
    View to handle both availability and booking details, and allow deletion if the user is the creator.
    """
    if listing_type == 'availability':
        listing = get_object_or_404(Availability, id=listing_id)
    elif listing_type == 'booking':
        listing = get_object_or_404(Booking, id=listing_id)
    else:
        return render(request, '404.html', status=404)  # Handle invalid listing type

    # Handle deletion
    
    if request.method == 'POST' and 'delete' in request.POST:
        can_delete = False
        if listing_type == 'availability':
            if (getattr(listing, 'artist', None) and listing.artist.user == request.user) or \
                (getattr(listing, 'venue', None) and listing.venue.user == request.user):
                can_delete = True
        elif listing_type == 'booking':
            if  (getattr(listing.availability, 'artist', None) and listing.availability.artist.user == request.user) or \
                (getattr(listing.availability, 'venue', None) and listing.availability.venue.user == request.user):
                can_delete = True

        if can_delete:
            listing.delete()
            return redirect('dashboard')
        else:
            return HttpResponseForbidden("You are not allowed to delete this listing.")
    # ...existing code...
    return render(request, 'listingdetail.html', {'listing': listing, 'listing_type': listing_type})


def handlebookingaction(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = Booking.objects.get(id=booking_id)
        availability = booking.availability

        if action == 'approve':
            # Create Event
            event = Events.objects.create(
                eventname=availability.description,
                eventdate=availability.start_time.date(),
                eventtime=availability.start_time.time(),
                location=availability.venue.location if availability.venue else None,
                eventdescription=availability.description,
                eventvenue=availability.venue if availability.venue else None,
                # Add other fields as needed - you might need to set a default value for ticketprice
                ticketprice=0.00  # Set an appropriate default value
            )
            # Optionally add artists to event
            if availability.artist:
                event.EventArtists.add(availability.artist)
            
            # Delete booking and availability
            booking.delete()
            availability.delete()
            
            # Redirect to the event detail page
            return redirect('event', event_id=event.id)
        elif action == 'reject':
            booking.delete()
            return redirect('dashboard')
        
        # Default fallback redirect
        return redirect('dashboard')
    
@login_required
@role_required(['artist', 'venue'])
def myevents(request):
    user = request.user
    events = []
    
    if user.role == 'artist' and hasattr(user, 'artist_user'):
        artist_events = Events.objects.filter(EventArtists=user.artist_user)
        events.extend(artist_events)
    
    if user.role == 'venue' and hasattr(user, 'venue_user'):
        venue_events = Events.objects.filter(eventvenue=user.venue_user)
        events.extend(venue_events)
    
    # Remove duplicates
    events = list(set(events))
    
    return render(request, 'myevents.html', {'events': events})