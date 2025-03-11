from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Fan)
admin.site.register(Artist)
admin.site.register(Venue)
admin.site.register(Doorman)