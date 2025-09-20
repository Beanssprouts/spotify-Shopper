from django.shortcuts import render

def quote(request):
    """Main resume page"""
    return render(request, 'aliciaLin/index.html')

def show_all(request):
    """Legacy show all page - redirect to main"""
    return render(request, 'aliciaLin/index.html')

def about(request):
    """About page"""
    return render(request, 'aliciaLin/about.html')
