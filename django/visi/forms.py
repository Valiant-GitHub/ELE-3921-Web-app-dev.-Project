from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import *
from django.forms import DateInput, TimeInput


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
        fields = ['start_time', 'end_time', 'date', 'description']
        widgets = {
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'}),
            'date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # Representing the user who is logged in and is creating the availability.
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the artist or venue based on the user's role
        if self.user.role == 'artist':
            instance.artist = self.user.artist_user
        elif self.user.role == 'venue':
            instance.venue = self.user.venue_user
        if commit:
            instance.save()
        return instance
    

class ChangeProfilePic(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profilepic"]


