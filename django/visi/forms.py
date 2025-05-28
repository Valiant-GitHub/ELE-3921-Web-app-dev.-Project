from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import *
from django.forms import DateInput, TimeInput
from django.forms import DateTimeInput


class SignUpForm(UserCreationForm):
    profilename = forms.CharField(max_length=100, required=True, label="Profile Name")
    bio = forms.CharField(widget=forms.Textarea, required=False, label="Bio")
    profilepic = forms.ImageField(required=False, label="Profile Picture")
    role = forms.ChoiceField(choices=User.choices, required=True, label="Role")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "profilename",
            "bio",
            "profilepic",
            "role",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.profilename = self.cleaned_data["profilename"]
        user.bio = self.cleaned_data["bio"]
        user.profilepic = self.cleaned_data["profilepic"]
        user.role = self.cleaned_data["role"]
        if not self.cleaned_data.get("profilepic"):
            user.profilepic = "profilepics/default.png"
        if commit:
            user.save()
        return user


class FanProfileForm(forms.ModelForm):
    class Meta:
        model = Fan
        fields = ["favartists", "genres"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["favartists"].queryset = User.objects.filter(
            artist_user__isnull=False
        )
        self.fields["favartists"].label_from_instance = lambda obj: obj.profilename


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ["artistimage", "genres"]


class VenueProfileForm(forms.ModelForm):
    address = forms.CharField(max_length=100, required=True, label="Address")
    zip = forms.CharField(max_length=6, required=True, label="Zip Code")
    city = forms.CharField(max_length=20, required=True, label="City")
    country = forms.CharField(max_length=20, required=True, label="Country")

    class Meta:
        model = Venue
        fields = [
            "address",
            "zip",
            "city",
            "country",
            "venuecapacity",
            "venueimage",
            "genres",
        ]

    def save(self, commit=True):
        venue = super().save(commit=False)
        location, created = Location.objects.get_or_create(
            address=self.cleaned_data["address"],
            zipcode=self.cleaned_data["zip"],
            city=self.cleaned_data["city"],
            country=self.cleaned_data["country"],
        )
        venue.location = location
        if commit:
            venue.save()
            self.save_m2m()
        return venue


class DoormanProfileForm(forms.ModelForm):
    class Meta:
        model = Doorman
        fields = []


# form for artists and venues to post availability, it should include start time, end time, date, location, description. the form automatically gets the user from the session and sets it to the artist or venue field.


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ["start_time", "end_time", "description"]
        widgets = {
            "start_time": DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")  # Get the logged-in user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the artist or venue based on the user's role
        if self.user.role == "artist":
            instance.artist = self.user.artist_user
            instance.venue = None  # Ensure venue is cleared
            instance.type = "artist"
        elif self.user.role == "venue":
            instance.venue = self.user.venue_user
            instance.artist = None  # Ensure artist is cleared
            instance.type = "venue"
        else:
            raise ValidationError("User role must be either 'artist' or 'venue'.")
        if commit:
            instance.save()
        return instance


class ChangeProfilePic(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profilepic"]


class Photoreel(forms.ModelForm):
    class Meta:
        model = Photoreel
        fields = ["image"]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["message"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = [
            "eventname",
            "eventdate",
            "eventtime",
            "location",
            "eventdescription",
            "eventimage",
            "eventvenue",
            "ticketprice",
            "genres",
        ]
        widgets = {
            "eventdate": forms.DateInput(attrs={"type": "date"}),
            "eventtime": forms.TimeInput(attrs={"type": "time"}),
        }
