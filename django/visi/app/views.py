import random
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from forms import *
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .utils import role_required, profile_required
from django.contrib import messages
from django.utils import timezone

# Create your views here.


# --View for home--#
def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html")
    if hasattr(request.user, "fan_user"):
        favartists = Artist.objects.filter(user__in=request.user.fan_user.favartists.all())
        eventsfromfollowed = Events.objects.filter(EventArtists__in=favartists).distinct()
        return render(request, "home.html", {"eventsfromfollowed": eventsfromfollowed})
    else:
        return render(request, "home.html")


# --View for events--#
def events(request):
    events = Events.objects.filter(eventdate__gte=timezone.now()).order_by("eventdate")
    pastevents = Events.objects.filter(eventdate__lt=timezone.now()).order_by(
        "-eventdate"
    )
    return render(request, "events.html", {"events": events, "pastevents": pastevents})


# --View for specific events--#
def event(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    return render(request, "event.html", {"event": event})


# --View for ticket purchasing--#
@login_required
def buyticket(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    if event.ticketsold >= event.eventvenue.venuecapacity:
        messages.error(request, "This event is sold out.")
        return redirect("event", event_id=event.id)
    if event.eventdate < timezone.now().date():
        messages.error(request, "This event has already passed.")
        return redirect("event", event_id=event.id)
    if request.method == "POST":
        if not hasattr(request.user, "fan_user"):
            messages.error(request, "Only fans can buy tickets.")
            return redirect("event", event_id=event.id)

        while True:
            ticketnumber = random.randint(10**15, 10**16 - 1)
            if not Tickets.objects.filter(ticketnumber=ticketnumber).exists():
                break

        ticket = Tickets.objects.create(
            event=event, fan=request.user.fan_user, ticketnumber=ticketnumber
        )

        event.ticketsold += 1
        event.save()

        return redirect("ticket", ticketnumber=ticket.id)
    return HttpResponse("Theres an issue.")


# --View for user profile--#
@profile_required
@login_required
def profile(request):
    return render(request, "profile.html")


# --View for signup--#
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("createprofile")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


# --View for ticket--#
@login_required
def ticketdetails(request, ticketnumber):
    ticket = get_object_or_404(Tickets, id=ticketnumber)
    if ticket.fan.user != request.user:
        return HttpResponse("You do not have permission to view this ticket.")

    return render(request, "ticket.html", {"ticket": ticket})


# --View for profile creation--#
@login_required
def createprofile(request):
    user = request.user
    # added a check to if the user already has a profile
    if (
        hasattr(user, "fan_user")
        or hasattr(user, "artist_user")
        or hasattr(user, "venue_user")
        or hasattr(user, "doorman_user")
    ):
        return redirect("profile")
    if user.role == "fan":
        form_class = FanProfileForm
    elif user.role == "artist":
        form_class = ArtistProfileForm
    elif user.role == "venue":
        form_class = VenueProfileForm
    elif user.role == "doorman":
        form_class = DoormanProfileForm
    else:
        return redirect("home")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect("home")
    else:
        form = form_class()

    return render(request, "profilecreation.html", {"form": form})


def save(self, commit=True):
    instance = super().save(commit=False)
    # Debugging: Print the user and their role
    print(f"Saving availability for user: {self.user}, role: {self.user.role}")

    # Set the artist or venue based on the user's role
    if self.user.role == "artist":
        instance.artist = self.user.artist_user
    elif self.user.role == "venue":
        instance.venue = self.user.venue_user
    else:
        print("User role is not artist or venue.")

    if commit:
        instance.save()
    return instance


# --View for posting availability--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def availability(request):
    if request.method == "POST":
        form = AvailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("availabilitysuccess")  # Redirect to a success page
    else:
        form = AvailabilityForm(user=request.user)

    return render(request, "availabilityform.html", {"form": form})


# --View for editing profile--#
@profile_required
@login_required
def editprofile(request):
    user = request.user
    profilepic = ChangeProfilePic(instance=user)

    if user.role == "fan":
        form = FanProfileForm
        profile = user.fan_user
    elif user.role == "artist":
        form = ArtistProfileForm
        profile = user.artist_user
    elif user.role == "venue":
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

    return render(
        request,
        "editprofile.html",
        {
            "profilepic": profilepic,
            "rolespecific": rolespecific,
        },
    )


# --View for success page for posting availability--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def availability_success(request):
    return render(request, "availabilitysuccess.html")


# --View for artist public profile--#
def artistprofile(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    events = Events.objects.filter(EventArtists=artist)
    return render(request, "artistprofile.html", {"artist": artist, "events": events})


# --View for venue public profile--#
def venueprofile(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    events = Events.objects.filter(eventvenue=venue)
    photoreel = venue.user.photoreel.all()
    return render(
        request,
        "venueprofile.html",
        {"venue": venue, "events": events, "photoreel": photoreel},
    )


# --View for availabilites--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def available(request):
    availabilities = Availability.objects.all().order_by("start_time")
    return render(request, "available.html", {"availabilities": availabilities})


# --View for requesting to book--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def requestbooking(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id)

    # Check if the user is trying to book their own availability
    is_owner = False

    if availability.artist and availability.artist.user == request.user:
        is_owner = True

    if availability.venue and availability.venue.user == request.user:
        is_owner = True

    if is_owner:
        messages.error(request, "You cannot book your own availability.")
        return redirect("available")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.availability = availability
            booking.save()
            return redirect("bookingsuccess")  # Redirect to a success page
    else:
        form = BookingForm()
    return render(request, "booking.html", {"form": form, "availability": availability})


# --View for showing successful booking--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def bookingsuccess(request):
    return render(request, "bookingsuccess.html")


# --View for dashboard--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def dashboard(request):
    # Get the logged-in user's availability slots and events
    if request.user.role == "artist":
        availabilities = Availability.objects.filter(artist__user=request.user)
        events = Events.objects.filter(EventArtists=request.user.artist_user)

    elif request.user.role == "venue":
        availabilities = Availability.objects.filter(venue__user=request.user)
        events = Events.objects.filter(eventvenue=request.user.venue_user)

    else:
        availabilities = Availability.objects.none()

    # Get all bookings for those availability slots
    bookings = Booking.objects.filter(availability__in=availabilities)

    # Prepare data for the calendar
    calendar_events = []
    for booking in bookings:
        color = (
            "green"
            if booking.status == "approved"
            else "orange" if booking.status == "pending" else "red"
        )
        calendar_events.append(
            {
                "title": booking.availability.description,
                "start": booking.availability.start_time.isoformat(),
                "end": booking.availability.end_time.isoformat(),
                "color": color,
            }
        )

    for event in events:
        calendar_events.append(
            {
                "title": event.eventname,
                "start": event.eventdate.isoformat(),
                "color": "blue",
            }
        )

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")  # 'approve' or 'reject'
        booking = get_object_or_404(Booking, id=booking_id)

        if action == "approve":
            booking.status = "approved"
        elif action == "reject":
            booking.status = "rejected"
        booking.save()

        return redirect("dashboard")  # Redirect back to the dashboard

    return render(
        request,
        "dashboard.html",
        {
            "availabilities": availabilities,
            "bookings": bookings,
            "calendar_events": calendar_events,  # Pass calendar data to the template
        },
    )


# --View for details on availability--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def listingdetail(request, listing_id, listing_type):
    """
    View to handle both availability and booking details, and allow deletion if the user is the creator.
    """
    if listing_type == "availability":
        listing = get_object_or_404(Availability, id=listing_id)
    elif listing_type == "booking":
        listing = get_object_or_404(Booking, id=listing_id)
    else:
        return render(request, "404.html", status=404)  # Handle invalid listing type

    # Handle deletion

    if request.method == "POST" and "delete" in request.POST:
        can_delete = False
        if listing_type == "availability":
            if (
                getattr(listing, "artist", None) and listing.artist.user == request.user
            ) or (
                getattr(listing, "venue", None) and listing.venue.user == request.user
            ):
                can_delete = True
        elif listing_type == "booking":
            if (
                getattr(listing.availability, "artist", None)
                and listing.availability.artist.user == request.user
            ) or (
                getattr(listing.availability, "venue", None)
                and listing.availability.venue.user == request.user
            ):
                can_delete = True

        if can_delete:
            listing.delete()
            return redirect("dashboard")
        else:
            return HttpResponseForbidden("You are not allowed to delete this listing.")
    # ...existing code...
    return render(
        request,
        "listingdetail.html",
        {"listing": listing, "listing_type": listing_type},
    )


# --View for booking--#
def handlebookingaction(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")
        booking = Booking.objects.get(id=booking_id)

        if action == "approve":
            # Store booking ID in session and redirect to event creation form
            request.session["approved_booking_id"] = booking_id
            return redirect("createevent")
        elif action == "reject":
            booking.delete()
            return redirect("dashboard")

    return redirect("dashboard")


# --View for showing users events--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def myevents(request):
    user = request.user
    events = []

    if user.role == "artist" and hasattr(user, "artist_user"):
        artist_events = Events.objects.filter(EventArtists=user.artist_user)
        events.extend(artist_events)

    if user.role == "venue" and hasattr(user, "venue_user"):
        venue_events = Events.objects.filter(eventvenue=user.venue_user)
        events.extend(venue_events)

    # Remove duplicates
    events = list(set(events))

    return render(request, "myevents.html", {"events": events})


# --View for creating event--#
@profile_required
@login_required
@role_required(["artist", "venue"])
def createevent(request):
    # Get the approved booking from session
    booking_id = request.session.get("approved_booking_id")
    if not booking_id:
        return redirect("dashboard")

    try:
        booking = Booking.objects.get(id=booking_id)
        availability = booking.availability
    except Booking.DoesNotExist:
        return redirect("dashboard")

    # Create a better event name combining artist and venue
    event_name = availability.description

    # Determine if the booking requester is different from the availability owner
    requesting_artist = None
    requesting_venue = None

    # If availability belongs to venue, requester might be artist
    if (
        availability.venue
        and booking.user.role == "artist"
        and hasattr(booking.user, "artist_user")
    ):
        requesting_artist = booking.user.artist_user

    # If availability belongs to artist, requester might be venue
    if (
        availability.artist
        and booking.user.role == "venue"
        and hasattr(booking.user, "venue_user")
    ):
        requesting_venue = booking.user.venue_user

    # Create artist+venue combo name
    actual_artist = requesting_artist or availability.artist
    actual_venue = requesting_venue or availability.venue

    if actual_artist and actual_venue:
        artist_name = (
            actual_artist.user.profilename
            if hasattr(actual_artist.user, "profilename")
            else actual_artist.user.username
        )
        venue_name = (
            actual_venue.user.profilename
            if hasattr(actual_venue.user, "profilename")
            else actual_venue.user.username
        )
        event_name = f"{artist_name} at {venue_name}"
    elif actual_artist:
        artist_name = (
            actual_artist.user.profilename
            if hasattr(actual_artist.user, "profilename")
            else actual_artist.user.username
        )
        event_name = f"{artist_name} performance"
    elif actual_venue:
        venue_name = (
            actual_venue.user.profilename
            if hasattr(actual_venue.user, "profilename")
            else actual_venue.user.username
        )
        event_name = f"Event at {venue_name}"

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            # Add artist if exists (either from availability or requester)
            if actual_artist:
                event.EventArtists.add(actual_artist)
            

            # Delete booking and availability
            booking.delete()
            availability.delete()
            # Clear session
            del request.session["approved_booking_id"]
            return redirect("event", event_id=event.id)
    else:
        # Prefill form with data from availability
        initial_data = {
            "eventname": event_name,
            "eventdate": availability.start_time.date(),
            "eventtime": availability.start_time.time(),
            "eventdescription": availability.description,
            "ticketprice": 0.00,  # Default value
        }

        # Auto-select the correct venue
        if actual_venue:
            initial_data["eventvenue"] = actual_venue.id

            # Auto-select the venue's location if it exists
            if hasattr(actual_venue, "location") and actual_venue.location:
                initial_data["location"] = actual_venue.location.id

        form = EventForm(initial=initial_data)

    return render(
        request,
        "createevent.html",
        {"form": form, "booking": booking, "availability": availability},
    )


# --View for photo uploads--#
@role_required("venue")
def photoupload(request):
    if request.method == "POST":
        form = Photoreel(request.POST, request.FILES)
        if form.is_valid():
            if "image" in request.FILES and request.FILES["image"]:
                photo = form.save(commit=False)
                photo.user = request.user
                photo.save()
                messages.success(
                    request, "Photo uploaded successfully! Upload another?"
                )
                return redirect("photoupload")
            else:
                messages.error(request, "Please select a file to upload.")
    else:
        form = Photoreel()
    return render(request, "uploadphoto.html", {"form": form})

# --View for ticket validation--#
@role_required("doorman")
def ticketvalidation(request):
    if request.method == "POST":
        ticket_number = request.POST.get("ticket_number")
        try:
            ticket = Tickets.objects.select_related("fan__user", "event").get(ticketnumber=ticket_number)
            event = ticket.event
            doorman = request.user.doorman_user
            if not event.authorized_doormen.filter(id=doorman.id).exists():
                messages.error(request, "You are not authorized to validate tickets for this event.")
                return redirect("ticketvalidation")
            return redirect("validateticket", ticket_id=ticket.id)
        except Tickets.DoesNotExist:
            messages.error(request, "Ticket not found.")
    return render(request, "ticketvalidation.html")

@role_required("doorman")
def validateticket(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    event = ticket.event
    doorman = request.user.doorman_user
    if not event.authorized_doormen.filter(id=doorman.id).exists():
        messages.error(request, "You are not authorized to validate tickets for this event.")
        return redirect("ticketvalidation")
    if request.method == "POST":
        if not ticket.is_used:
            ticket.is_used = True
            ticket.save()
            messages.success(request, "Ticket validated")
        else:
            messages.info(request, "Ticket was already used.")
    return render(request, "validateticket.html", {"ticket": ticket})