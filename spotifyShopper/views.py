import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import SpotifyUser, Playlist, UserPlaylist
import logging
logger = logging.getLogger(__name__)
import sys


def home(request):
    """Landing page - login or go to shop"""
    if request.user.is_authenticated:
        try:
            SpotifyUser.objects.get(user=request.user)
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
    """Handle Spotify OAuth callback with better debugging"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    print(f"Callback received - Code: {bool(code)}, Error: {error}")
    
    if error:
        print(f"Spotify OAuth error: {error}")
        messages.error(request, f'Spotify authorization failed: {error}')
        return redirect('spotify_home')
    
    if not code:
        print("No authorization code received")
        messages.error(request, 'No authorization code received')
        return redirect('spotify_home')

    # Exchange code for token
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    }
    
    print(f"Token request data: {token_data}")
    
    response = requests.post(token_url, data=token_data)
    
    print(f"Token response status: {response.status_code}")
    print(f"Token response: {response.text}")
    
    if response.status_code != 200:
        print(f"Token exchange failed: {response.text}")
        messages.error(request, f'Failed to get Spotify token: {response.text}')
        return redirect('spotify_home')

    data = response.json()
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    expires_in = data.get('expires_in')

    if not access_token:
        print("No access token in response")
        messages.error(request, 'No access token received')
        return redirect('spotify_home')

    # Get user profile
    profile_headers = {'Authorization': f'Bearer {access_token}'}
    print(f"Profile request headers: {profile_headers}")
    
    profile_response = requests.get(
        'https://api.spotify.com/v1/me',
        headers=profile_headers
    )

    print(f"Profile response status: {profile_response.status_code}")
    print(f"Profile response: {profile_response.text}")

    if profile_response.status_code != 200:
        print(f"Profile request failed: {profile_response.text}")
        messages.error(request, f'Failed to get Spotify profile: {profile_response.text}')
        return redirect('spotify_home')

    profile = profile_response.json()
    print(f"Profile data: {profile}")

    # Rest of your existing code...
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
    print("=== SHOP VIEW CALLED ===", file=sys.stderr, flush=True)
    print(f"User: {request.user.username}", file=sys.stderr, flush=True)
    
    try:
        spotify_user = SpotifyUser.objects.get(user=request.user)
        print(f"Found Spotify user: {spotify_user.display_name}", file=sys.stderr, flush=True)
        print(f"Token expires: {spotify_user.token_expiry}", file=sys.stderr, flush=True)
    except SpotifyUser.DoesNotExist:
        print("SpotifyUser does not exist", file=sys.stderr, flush=True)
        messages.error(request, 'Please connect your Spotify account first')
        return redirect('spotify_home')

    try:
        print("About to call get_featured_playlists", file=sys.stderr, flush=True)
        playlists = get_featured_playlists(spotify_user)
        print(f"Got {len(playlists)} playlists", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"ERROR in get_featured_playlists: {e}", file=sys.stderr, flush=True)
        playlists = []
    
    cart = request.session.get('cart', [])
    return render(request, 'spotifyShopper/shop.html', {
        'playlists': playlists,
        'cart_count': len(cart),
        'spotify_user': spotify_user
    })


def get_featured_playlists(spotify_user):
    """Fetch playlists from Spotify API using categories"""
    import sys
    print(f"=== GET_FEATURED_PLAYLISTS CALLED ===", file=sys.stderr, flush=True)
    
    if spotify_user.token_expiry <= timezone.now():
        refresh_user_token(spotify_user)

    headers = {'Authorization': f'Bearer {spotify_user.spotify_token}'}
    
    # Since featured playlists don't work, get playlists from popular categories
    categories_url = 'https://api.spotify.com/v1/browse/categories?limit=3&market=US'
    print(f"Getting categories: {categories_url}", file=sys.stderr, flush=True)
    
    categories_response = requests.get(categories_url, headers=headers)
    print(f"Categories response: {categories_response.status_code}", file=sys.stderr, flush=True)
    
    if categories_response.status_code != 200:
        return []
    
    categories_data = categories_response.json()
    categories = categories_data.get('categories', {}).get('items', [])
    print(f"Found {len(categories)} categories", file=sys.stderr, flush=True)
    
    all_playlists = []
    
    for category in categories[:2]:  # Just use first 2 categories to avoid too many API calls
        category_id = category['id']
        category_name = category['name']
        print(f"Getting playlists for category: {category_name}", file=sys.stderr, flush=True)
        
        # Get playlists for this category
        playlist_url = f'https://api.spotify.com/v1/browse/categories/{category_id}/playlists?limit=10&market=US'
        playlist_response = requests.get(playlist_url, headers=headers)
        print(f"Category {category_name} playlists response: {playlist_response.status_code}", file=sys.stderr, flush=True)
        
        if playlist_response.status_code == 200:
            playlist_data = playlist_response.json()
            playlists_items = playlist_data.get('playlists', {}).get('items', [])
            print(f"Found {len(playlists_items)} playlists in {category_name}", file=sys.stderr, flush=True)
            
            for sp in playlists_items:
                try:
                    playlist, created = Playlist.objects.get_or_create(
                        spotify_id=sp['id'],
                        defaults={
                            'name': sp['name'],
                            'description': sp.get('description', ''),
                            'image_url': sp['images'][0]['url'] if sp.get('images') else '',
                            'track_count': sp['tracks']['total'],
                            'owner_name': sp['owner']['display_name'],
                            'owner_id': sp['owner']['id']
                        }
                    )
                    all_playlists.append(playlist)
                    if created:
                        print(f"Created playlist: {playlist.name}", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"Error processing playlist: {e}", file=sys.stderr, flush=True)
                    continue
        else:
            print(f"Failed to get playlists for {category_name}: {playlist_response.text[:100]}", file=sys.stderr, flush=True)

    print(f"Returning {len(all_playlists)} total playlists", file=sys.stderr, flush=True)
    return all_playlists


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
    cart = request.session.get('cart', [])
    if playlist_id in cart:
        cart.remove(playlist_id)
        request.session['cart'] = cart
        messages.success(request, 'Removed from cart!')
    return redirect('cart')


@login_required
def view_cart(request):
    cart_ids = request.session.get('cart', [])
    playlists = Playlist.objects.filter(spotify_id__in=cart_ids)

    return render(request, 'spotifyShopper/cart.html', {
        'playlists': playlists,
        'cart_count': len(cart_ids)
    })


@login_required
def purchase_cart(request):
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
        if follow_playlist_on_spotify(spotify_user, playlist.spotify_id):
            UserPlaylist.objects.get_or_create(
                spotify_user=spotify_user,
                playlist=playlist
            )
            followed_count += 1

    request.session['cart'] = []
    messages.success(request, f'Successfully followed {followed_count} playlists!')
    return redirect('my_playlists')


def follow_playlist_on_spotify(spotify_user, playlist_id):
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
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('spotify_home')


def test_spotify(request):
    test_token = "YOUR_TEST_TOKEN_HERE"
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get('https://api.spotify.com/v1/browse/featured-playlists?limit=5', headers=headers)

    if response.status_code == 200:
        playlists = response.json().get('playlists', {}).get('items', [])
        return render(request, 'spotifyShopper/test.html', {'playlists': playlists})
    else:
        return render(request, 'spotifyShopper/test.html', {'error': 'API failed'})
