from django.db import models
from django.contrib.auth.models import User

class SpotifyUser(models.Model):
    """Extension of Django User for Spotify data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=100, unique=True)
    spotify_token = models.CharField(max_length=500, blank=True, null=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.display_name or self.spotify_id}"

class Playlist(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    track_count = models.IntegerField(default=0)
    owner_name = models.CharField(max_length=100)
    owner_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} by {self.owner_name}"

class UserPlaylist(models.Model):
    """Track which playlists a user has 'purchased' (followed)"""
    spotify_user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['spotify_user', 'playlist']