from django.shortcuts import render
import random

# Global lists of quotes and images
quotes = [
    "Innovation is seeing what everybody has seen and thinking what nobody has thought.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
]

images = [
    "https://example.com/alicia1.jpg",
    "https://example.com/alicia2.jpg", 
    "https://example.com/alicia3.jpg",
]

def quote(request):
    """Main page with modern scrolling design"""
    context = {
        'quotes': quotes,
        'images': images,
    }
    return render(request, 'aliciaLin/index.html', context)

def show_all(request):
    """Legacy show all page"""
    context = {
        'quotes': quotes,
        'images': images,
    }
    return render(request, 'aliciaLin/show_all.html', context)

def about(request):
    """About page"""
    return render(request, 'aliciaLin/about.html')