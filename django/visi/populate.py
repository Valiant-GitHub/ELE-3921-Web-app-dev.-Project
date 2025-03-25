from django.contrib.auth import get_user_model
from django.db import transaction
from app.models import User, Genre, Fan, Artist, Venue, Location, Events, Tickets, EventArtists

UserModel = get_user_model()

@transaction.atomic
def populate_database():
    # Create genres
    genres = [
        Genre.objects.create(genrename="Rock", code="ROCK"),
        Genre.objects.create(genrename="Pop", code="POP"),
        Genre.objects.create(genrename="Jazz", code="JAZZ"),
        Genre.objects.create(genrename="Classical", code="CLASS"),
    ]

    # Create users
    users = [
        UserModel.objects.create_user(username="fan1", password="1", role="fan", profilename="Fan One"),
        UserModel.objects.create_user(username="artist1", password="1", role="artist", profilename="Artist One"),
        UserModel.objects.create_user(username="venue1", password="1", role="venue", profilename="Venue One"),
        UserModel.objects.create_user(username="doorman1", password="1", role="doorman", profilename="Doorman One"),
    ]

    # Create fans
    fan1 = Fan.objects.create(user=users[0])
    fan1.genres.set(genres[:2])  # Fan follows Rock and Pop genres

    # Create artists
    artist1 = Artist.objects.create(user=users[1])
    artist1.genres.set(genres[:1])  # Artist performs Rock genre

    # Create location
    location = Location.objects.create(
        address="123 Main St", city="Oslo", country="Norway", zipcode="12345"
    )

    # Create venues
    venue1 = Venue.objects.create(
        user=users[2],
        location=location,
        venuecapacity=500,
    )
    venue1.genres.set(genres[:3])  # Venue supports Rock, Pop, and Jazz genres

    # Create events
    event1 = Events.objects.create(
        eventname="Rock Night",
        eventdate="2025-04-01",
        eventtime="19:00:00",
        location=location,
        eventdescription="A night of rock music.",
        eventvenue=venue1,
        ticketprice=50.00,
    )
    event1.genres.set(genres[:1])  # Event is Rock genre
    EventArtists.objects.create(artist=artist1, event=event1)

    # Create tickets
    Tickets.objects.create(event=event1, fan=fan1, ticketnumber=1)

    print("Database populated successfully!")

# Run the function
if __name__ == "__main__":
    populate_database()