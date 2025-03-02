from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    choices = [
        ("fan", "Fan"),
        ("artist", "Artist"),
        ("venue", "Venue"),
    ]
    role = models.CharField(max_length=100, choices=choices, default="fan")
    profilepic = models.ImageField(upload_to="media/profilepics/", default="media/profilepics/default.png", null=True, blank=True)    
    def __str__(self):
        return self.username