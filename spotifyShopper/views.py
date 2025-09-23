import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import SpotifyUser, Playlist, UserPlaylist

def home(request):
    """Landing page - login or go to shop"""
    if request.user.is_authenticated:
        try:
            spotify_user = SpotifyUser.objects.get(user=request.user)
            return redirect('shop')
        except SpotifyUser.DoesNotExist:
            pass
    return render(request, 'spotifyShopper/home.html')

def spotify_login(request):
    """Redirect to Spotify OAuth"""
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'
    auth_url = (
        f'https://accounts.spotify.com/authorize'
        f'?response_type=code'
        f'&client_id={settings.SPOTIFY_CLIENT_ID}'
        f'&redirect_uri={settings.SPOTIFY_REDIRECT_URI}'
        f'&scope={scope}'
    )
    return redirect(auth_url)

def spotify_callback(request):
    """Handle Spotify OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Spotify authorization failed')
        return redirect('spotify_home')
    
    # Exchange code for token
    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })
    
    if response.status_code != 200:
        messages.error(request, 'Failed to get Spotify token')
        return redirect('spotify_home')
        
    data = response.json()
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    expires_in = data.get('expires_in')
    
    # Get user profile
    profile_response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if profile_response.status_code != 200:
        messages.error(request, 'Failed to get Spotify profile')
        return redirect('spotify_home')
    
    profile = profile_response.json()
    
    # Create or get Django user
    django_user, created = User.objects.get_or_create(
        username=profile['id'],
        defaults={
            'email': profile.get('email', ''),
            'first_name': profile.get('display_name', '')
        }
    )
    
    # Create or update SpotifyUser
    spotify_user, created = SpotifyUser.objects.get_or_create(
        user=django_user,
        defaults={'spotify_id': profile['id']}
    )
    
    spotify_user.spotify_token = access_token
    spotify_user.refresh_token = refresh_token
    spotify_user.token_expiry = timezone.now() + timedelta(seconds=expires_in)
    spotify_user.display_name = profile.get('display_name', '')
    spotify_user.save()
    
    login(request, django_user)
    messages.success(request, f'Welcome {spotify_user.display_name}!')
    return redirect('shop')

@login_required
def shop(request):
    """Browse playlists"""
    try:
        spotify_user = SpotifyUser.objects.get(user=request.user)
    except SpotifyUser.DoesNotExist:
        messages.error(request, 'Please connect your Spotify account first')
        return redirect('spotify_home')
    
    # Get featured playlists from Spotify
    playlists = get_featured_playlists(spotify_user)
    cart = request.session.get('cart', [])
    
    return render(request, 'spotifyShopper/shop.html', {
        'playlists': playlists,
        'cart_count': len(cart),
        'spotify_user': spotify_user
    })

def get_featured_playlists(spotify_user):
    """Fetch playlists from Spotify API"""
    if spotify_user.token_expiry <= timezone.now():
        refresh_user_token(spotify_user)
    
    headers = {'Authorization': f'Bearer {spotify_user.spotify_token}'}
    response = requests.get(
        'https://api.spotify.com/v1/browse/featured-playlists?limit=20',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Spotify API error: {response.status_code}")
        return []
    
    spotify_playlists = response.json().get('playlists', {}).get('items', [])
    playlists = []
    
    for sp in spotify_playlists:
        # Save to our database
        playlist, created = Playlist.objects.get_or_create(
            spotify_id=sp['id'],
            defaults={
                'name': sp['name'],
                'description': sp.get('description', ''),
                'image_url': sp['images'][0]['url'] if sp['images'] else '',
                'track_count': sp['tracks']['total'],
                'owner_name': sp['owner']['display_name'],
                'owner_id': sp['owner']['id']
            }
        )
        playlists.append(playlist)
    
    return playlists

def refresh_user_token(spotify_user):
    """Refresh expired token"""
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': spotify_user.refresh_token,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })
    
    if response.status_code == 200:
        data = response.json()
        spotify_user.spotify_token = data['access_token']
        spotify_user.token_expiry = timezone.now() + timedelta(seconds=data['expires_in'])
        spotify_user.save()

@login_required
def add_to_cart(request, playlist_id):
    """Add playlist to session cart"""
    cart = request.session.get('cart', [])
    if playlist_id not in cart:
        cart.append(playlist_id)
        request.session['cart'] = cart
        messages.success(request, 'Added to cart!')
    else:
        messages.info(request, 'Already in cart!')
    return redirect('shop')

@login_required
def remove_from_cart(request, playlist_id):
    """Remove from cart"""
    cart = request.session.get('cart', [])
    if playlist_id in cart:
        cart.remove(playlist_id)
        request.session['cart'] = cart
        messages.success(request, 'Removed from cart!')
    return redirect('cart')

@login_required
def view_cart(request):
    """View cart contents"""
    cart_ids = request.session.get('cart', [])
    playlists = Playlist.objects.filter(spotify_id__in=cart_ids)
    
    return render(request, 'spotifyShopper/cart.html', {
        'playlists': playlists,
        'cart_count': len(cart_ids)
    })

@login_required
def purchase_cart(request):
    """Follow all playlists in cart"""
    if request.method != 'POST':
        return redirect('cart')
    
    try:
        spotify_user = SpotifyUser.objects.get(user=request.user)
    except SpotifyUser.DoesNotExist:
        messages.error(request, 'Spotify account not found')
        return redirect('spotify_home')
    
    cart_ids = request.session.get('cart', [])
    if not cart_ids:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    playlists = Playlist.objects.filter(spotify_id__in=cart_ids)
    followed_count = 0
    
    for playlist in playlists:
        # Follow on Spotify
        if follow_playlist_on_spotify(spotify_user, playlist.spotify_id):
            # Save to our database
            UserPlaylist.objects.get_or_create(
                spotify_user=spotify_user,
                playlist=playlist
            )
            followed_count += 1
    
    # Clear cart
    request.session['cart'] = []
    
    messages.success(request, f'Successfully followed {followed_count} playlists!')
    return redirect('my_playlists')

def follow_playlist_on_spotify(spotify_user, playlist_id):
    """Follow a playlist on Spotify"""
    if spotify_user.token_expiry <= timezone.now():
        refresh_user_token(spotify_user)
    
    headers = {'Authorization': f'Bearer {spotify_user.spotify_token}'}
    response = requests.put(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/followers',
        headers=headers
    )
    
    return response.status_code == 200

@login_required
def my_playlists(request):
    """View purchased playlists"""
    try:
        spotify_user = SpotifyUser.objects.get(user=request.user)
        user_playlists = UserPlaylist.objects.filter(spotify_user=spotify_user).order_by('-followed_at')
    except SpotifyUser.DoesNotExist:
        user_playlists = []
    
    return render(request, 'spotifyShopper/my_playlists.html', {
        'user_playlists': user_playlists,
        'cart_count': len(request.session.get('cart', []))
    })

@login_required
def logout_view(request):
    """Logout user"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('spotify_home')

# Add this simple test view to your views.py
def test_spotify(request):
    """Test Spotify API with hardcoded token"""
    # You can get a temporary token from https://developer.spotify.com/console/
    test_token = "YOUR_TEST_TOKEN_HERE"  # Get from Spotify web console
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get('https://api.spotify.com/v1/browse/featured-playlists?limit=5', headers=headers)
    
    if response.status_code == 200:
        playlists = response.json().get('playlists', {}).get('items', [])
        return render(request, 'spotifyShopper/test.html', {'playlists': playlists})
    else:
        return render(request, 'spotifyShopper/test.html', {'error': 'API failed'})