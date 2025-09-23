# File: urls.py
# Author: Alicia beans@bu.edu, 9/16/2025
# Description: URL configuration for the Borat restaurant of the Day application.
# Maps URLs to their corresponding view functions.

from django.urls import path
from . import views

# File: restaurant/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('order/', views.order, name='order'),
    path('notaconfirmation/', views.confirmation, name='confirmation'),  # ← Fixed name
    path('level2/', views.level2, name='level2'),
]