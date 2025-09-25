from django.contrib import admin
from django.urls import path, include
from spotifyShopper import views as shopper_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('callback/', shopper_views.spotify_callback, name='spotify_callback'),
    path('', include('spotifyShopper.urls')),
]
