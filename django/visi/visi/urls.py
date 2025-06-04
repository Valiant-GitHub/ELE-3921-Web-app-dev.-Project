"""
URL configuration for visi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("events/", views.events, name="events"),
    path("events/event/<int:event_id>/", views.event, name="event"),
    path("events/event/<int:event_id>/buy/", views.buyticket, name="buyticket"),
    path("profile/", views.profile, name="profile"),
    path("profile/ticket/<int:ticketnumber>", views.ticketdetails, name="ticket"),
    path('profile/edit/', views.editprofile, name="editprofile"),
    path("signup/", views.signup, name="signup"),
    path("createprofile/", views.createprofile, name="createprofile"),
    path("availabilityform/", views.availability, name="availabilityform"),
    path('availabilitysuccess/', views.availability_success, name='availabilitysuccess'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("artist/<int:artist_id>/", views.artistprofile, name="artistprofile"),
    path("venue/<int:venue_id>/", views.venueprofile, name="venueprofile"),
    path('availability/<int:availability_id>/request/', views.requestbooking, name='requestbooking'),
    path('available/', views.available, name='available'),
    path('availability/<int:availability_id>/request/', views.requestbooking, name='requestbooking'),
    path('bookingsuccess/', views.bookingsuccess, name='bookingsuccess'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Add this line
    path('listing/<str:listing_type>/<int:listing_id>/', views.listingdetail, name='listingdetail'),
    path('bookingaction/', views.handlebookingaction, name='bookingaction'),
    path('myevents/', views.myevents, name='myevents'),
    path('createevent/', views.createevent, name='createevent'),
    path('bookingaction/', views.handlebookingaction, name='bookingaction'),
    path('venue/upload-photo/', views.photoupload, name='photoupload'),
    path('venue/delete-photo/<int:photo_id>/', views.deletephoto, name='deletephoto'),   
    path("ticketvalidation/", views.ticketvalidation, name="ticketvalidation"),
    path("ticketvalidation/validate/<int:ticket_id>", views.validateticket, name="validateticket"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)