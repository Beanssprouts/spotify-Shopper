# File: views.py
# Author: Alicia (beans@bu.edu), 9/11/2025
# Description: Views for the Borat Quote of the Day application.
# Contains view functions for displaying random quotes, all quotes, and about page.

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import random

# Global lists of quotes and images (all from the same person)
QUOTES = [
    '"He is my neighbor Nursultan Tuliagby. \nHe is pain in my assholes. I get a window from a glass, \nhe must get a window from a glass. \nI get a step, he must get a step. \nI get a clock radio, he cannot afford. Great success!"',
    '"This is Urkin, the town rapist. Naughty, naughty!"',
    '"When you chase a dream, \nespecially one with plastic chests, \nyou sometimes do not see what is right in front of you."',
    '"Wawaweewa!"',
    '"Oh da baby!"'
]

IMAGES = [
    "https://m.media-amazon.com/images/I/61dtddh2aOL._UY1000_.jpg",
    "https://www.media.hw-static.com/media/2016/10/borat-20th-century-fox-103116.jpg",
    "https://www.dispatch.com/gcdn/authoring/2017/11/15/NCOD/ghows-OH-857cbdaf-4264-4814-87a8-4c4f10b9cc6d-543bc385.jpeg?width=660&height=448&fit=crop&format=pjpg&auto=webp",
    "https://www.maxim.com/cdn-cgi/image/quality=80,format=auto,onerror=redirect,metadata=none/wp-content/uploads/2021/05/borat-mankini-scaled.jpg",
    "https://static01.nyt.com/images/2020/10/23/arts/borat1/borat1-videoSixteenByNineJumbo1600.jpg",
    "https://live-production.wcms.abc-cdn.net.au/df5f3c2c9de9acc46677ce0bfff43248?impolicy=wcms_crop_resize&cropH=1080&cropW=1918&xPos=1&yPos=0&width=862&height=485", 
    "https://akns-images.eonline.com/eol_images/Entire_Site/2020926/rs_634x1024-201026153109-634-13sacha-baron-cohen-wild-moments.ls.jpg?fit=around%7C776:1254&output-quality=90&crop=776:1254;center,top",
    "https://static01.nyt.com/images/2020/10/23/arts/23borat-moments1/23borat-moments1-mediumSquareAt3X.jpg",
    "https://variety.com/wp-content/uploads/2025/06/MCDBORA_FE045.jpg?w=1000&h=667&crop=1"
]

def quote(request):
    """Display one random quote and image."""
    # Select a random quote from the QUOTES list
    selected_quote = random.choice(QUOTES)
    
    # Select a random image from the IMAGES list
    selected_image = random.choice(IMAGES)
    
    # Create context dictionary to pass data to template
    context = {
        'quote': selected_quote,
        'image': selected_image,
    }
    return render(request, 'quotes/quote.html', context)

def show_all(request):
    """Display all quotes and images."""
    # Create context dictionary with all quotes and images
    context = {
        'quotes': QUOTES,
        'images': IMAGES,
    }
    return render(request, 'quotes/show_all.html', context)

def about(request):
    """Display about page."""
    # Create context dictionary with person information
    context = {
        'person_name': 'Borat',
        'bio': 'its Borat',
    }
    return render(request, 'quotes/about.html', context)