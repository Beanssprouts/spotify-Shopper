# File: urls.py
# Author: Alicia beans@bu.edu, 9/11/2025
# Description: URL configuration for the Borat Quote of the Day application.
# Maps URLs to their corresponding view functions.

from django.urls import path
from . import views

# URL patterns for the quotes application
urlpatterns = [
    # Root URL, displays random quote
    path('', views.quote, name='quote'),
    
    # Quote URL, displays random quote
    path('quote/', views.quote, name='quote'),
    
    # Show all URL, displays all quotes and images
    path('show_all/', views.show_all, name='show_all'),
    
    # About URL, displays about page
    path('about/', views.about, name='about'),
]