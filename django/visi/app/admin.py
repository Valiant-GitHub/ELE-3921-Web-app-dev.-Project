from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Fan)
admin.site.register(Doorman)
admin.site.register(Artist)
admin.site.register(Venue)
admin.site.register(Photoreel)
admin.site.register(Location)
admin.site.register(Availability)
admin.site.register(Events)
admin.site.register(EventArtists)
admin.site.register(Tickets)