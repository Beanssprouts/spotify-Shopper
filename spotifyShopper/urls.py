from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='spotify_home'),
    path('login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<str:playlist_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:playlist_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('purchase/', views.purchase_cart, name='purchase_cart'),
    path('my-playlists/', views.my_playlists, name='my_playlists'),
    path('logout/', views.logout_view, name='spotify_logout'),
]