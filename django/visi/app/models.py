from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.

class User(AbstractUser):
    choices = [
        ("fan", "Fan"),
        ("artist", "Artist"),
        ("venue", "Venue"),
        ("doorman", "Doorman"),
    ]
    role = models.CharField(max_length=100, choices=choices, default="fan")
    profilename = models.CharField(max_length=100) # Name on profile different from username and full name
    bio = models.TextField(max_length=1000, null=True, blank=True)
    profilepic = models.ImageField(upload_to="profilepics/", default="profilepics/default.png", null=True, blank=True)    
    def __str__(self):
        return self.username

class Genre(models.Model):
    genrename = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.genrename

class Fan(models.Model):
    # One-to-one relationship with user and cascade to delete the fan if the user is deleted.
    # Related name is used to access the fan object from the user object.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="fan_user")
    favartists = models.ManyToManyField(User, related_name="fan_favartists")
    eventsattended = models.ManyToManyField("Events", through="Tickets", related_name="fan_eventsattended")
    # The genres the user follows for events.
    genres = models.ManyToManyField(Genre, related_name="fans", blank=True)
    def __str__(self):
        return self.user.profilename

class Doorman(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doorman_user")    
    def __str__(self):
        return self.user.profilename


class Artist(models.Model):
    # One-to-one relationship with user and cascade to delete the artist if the user is deleted.
    # Related name is used to access the artist object from the user object.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="artist_user")
        # Artist image could be used to differentiate between a user image and an artist's promo image.
    artistimage = models.ImageField(upload_to="artistpics/", default="artistpics/default.png", null=True, blank=True)
    artistfans = models.ManyToManyField(User, related_name="artist_fans", blank=True)
    genres = models.ManyToManyField(Genre, related_name="artists", blank=True)
    def __str__(self):
        return self.user.profilename
    

class Venue(models.Model):
    # One-to-one relationship with user and cascade to delete the venue if the user is deleted.
    # Related name is used to access the venue object from the user object.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="venue_user")
    location = models.ForeignKey("Location", on_delete=models.CASCADE, related_name="venue_location")
    venuecapacity = models.IntegerField()
    venueimage = models.ImageField(upload_to="venuepics/", default="venuepics/default.png", null=True, blank=True)
    venuefans = models.ManyToManyField(User, related_name="venue_fans", blank=True)
    genres = models.ManyToManyField(Genre, related_name="venues", blank=True)
    def __str__(self):
        return self.user.profilename
    

class Photoreel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="photoreel")
    image = models.ImageField(upload_to="reels/",  null=True, blank=True)
    def __str__(self):
        return self.image.url

#location model for venues and events, helps adhere to relational database principles
class Location(models.Model):
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}, {self.zipcode}"
 
class Availability(models.Model):
    TYPE_CHOICES = [
        ('artist', 'Artist'),
        ('venue', 'Venue'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name="availability_artist")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True, blank=True, related_name="availability_venue")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(artist__isnull=False, venue__isnull=True) |
                    models.Q(artist__isnull=True, venue__isnull=False)
                ),
                name="artist_or_venue_only"
            )
        ]
       

class Events(models.Model):
    eventname = models.CharField(max_length=100)
    eventdate = models.DateField()
    eventtime = models.TimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="events")
    eventdescription = models.TextField()
    eventimage = models.ImageField(upload_to="eventpics/", default="eventpics/default.png", null=True, blank=True)
    EventArtists = models.ManyToManyField(Artist, through="EventArtists", related_name="event_artists")
    eventvenue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="event_venue")
    ticketsold = models.IntegerField(default=0)
    # Not sure if we should create the metric for the progress bar here as a function or in the view.
    ticketprice = models.DecimalField(max_digits=5, decimal_places=2)
    genres = models.ManyToManyField(Genre, related_name="events")
    authorized_doormen = models.ManyToManyField(Doorman, related_name="events", blank=True)
    def __str__(self):
        return self.eventname

class EventArtists(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="event_artist")
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="event_artist")
    def __str__(self):
        return f"{self.artist.user.profilename} at {self.event.eventname}"

class Tickets(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="tickets")
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name="tickets")
    ticketnumber = models.IntegerField()
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f"Ticket {self.ticketnumber} for {self.fan.user.profilename} to {self.event.eventname}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booking")
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name="booking")
    message = models.TextField(blank=True, null=True, max_length=1000)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.availability}"


#class Reviews(models.Model):
#class Merchandise
#class Orders
#class OrderItems