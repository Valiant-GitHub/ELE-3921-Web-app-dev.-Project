from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import *

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