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
        fields = ['username', 'email', 'password1', 'password2', 'profilename', 'bio', 'profilepic', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.profilename = self.cleaned_data['profilename']
        user.bio = self.cleaned_data['bio']
        user.profilepic = self.cleaned_data['profilepic']
        user.role = self.cleaned_data['role']
        if not self.cleaned_data.get('profilepic'):
            user.profilepic = "profilepics/default.png"
        if commit:
            user.save()
        return user
    
class FanProfileForm(forms.ModelForm):
    class Meta:
        model = Fan
        fields = ['favartists', 'genres']

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['artistimage', 'genres']

class VenueProfileForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['venuecapacity', 'location', 'venueimage', 'genres']

class DoormanProfileForm(forms.ModelForm):
    class Meta:
        model = Doorman
        fields = [] 

#form for artists and venues to post availability, it should include start time, end time, date, location, description. the form automatically gets the user from the session and sets it to the artist or venue field.


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time', 'description']  # Exclude artist and venue from the form
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Get the logged-in user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # Set artist or venue based on the user's role
        if self.user.role == 'artist':
            self.instance.artist = self.user.artist_user
            print(f"Debug: Set artist in form clean: {self.instance.artist}")
        elif self.user.role == 'venue':
            self.instance.venue = self.user.venue_user
            print(f"Debug: Set venue in form clean: {self.instance.venue}")
        else:
            print("Debug: User role is not artist or venue.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        print(f"Debug: Saving availability for user: {self.user}, role: {self.user.role}")
        # Automatically set artist or venue based on the user's role
        if self.user.role == 'artist':
            instance.artist = self.user.artist_user
            print(f"Debug: Set artist: {instance.artist}")
        elif self.user.role == 'venue':
            instance.venue = self.user.venue_user
            print(f"Debug: Set venue: {instance.venue}")
        else:
            print("Debug: User role is not artist or venue.")
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
