from django.shortcuts import render
import random
import datetime
import math

"""The Daily Specials that are being rotated amongst"""
dailySpecials = [
        {'name': 'Meatloaf', 'price': 8.99}, 
        {'name': 'Fish and Chips', 'price': 10.99}, 
        {'name': 'The Wednesday Thing', 'price': 11.11}, 
        {'name': 'Todays Fresh Catch', 'price': 14.44, 'description': '(caught in the office building)' },
        {'name': 'Your Usual', 'price': 14.99, 'description': '(you dont have a usual)'}
    ]

def main(request): 
    """displays the Main Page with an image and a description of the pizzeria"""
    selectedImage = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6e5Nst67dlvLVibosC99m7EGUfA8l4eVUUg&s"

    context = {
        'image': selectedImage
    }
    return render(request, 'restaurant/main.html', context)

def order(request): 
    """this displays the ordering page"""
    menuItems = [
        {'name': 'Chicken Parmesan', 'price': 15.99},
        {'name': 'Steak and Cheese Sub', 'price': 11.49},
        {'name': 'BLT Sandwich', 'price': 8.99},
        {'name': 'Grilled Chicken Caesar Salad', 'price': 10.99},
        {'name': 'Freddy\'s Supreme Pizza', 'price': 12.99},
        {'name': 'Today\'s soup', 'price': 4.99, 'description':'(ask what day it is)'},
        {'name': 'Club Sandwich', 'price': 9.49},
        {'name': 'Chefs Reccomendation', 'price': '?.99', 'description': '(chef has been gone for weeks)'},
        {'name': 'The Humming', 'price': "∞"},
        {'name': 'The Taste of Yellow', 'price': 4.99},
        {'name': 'The Exit', 'price': 0.00, 'description': '(SOLD OUT)','disabled': True},
        {'name': 'The Exit', 'price': 0.00, 'description': '(SOLD OUT)','disabled': True},
        {'name': 'The Exit', 'price': 0.00, 'description': '(SOLD OUT)','disabled': True},
        {'name': 'The Exit', 'price': 0.00, 'description': '(SOLD OUT)','disabled': True},
        {'name': 'The Exit', 'price': 0.00, 'description': '(SOLD OUT)','disabled': True},
        {'name': 'The Way Back', 'price': '∞∞.∞∞', 'description': '(payment plans available)'},
    ]

    selectedSpecials = random.choice(dailySpecials)

    context = {
        'entrees': menuItems, 
        'specials': selectedSpecials,
    }
    return render(request, 'restaurant/order.html', context)

def confirmation(request): 
    """displays after the order has been submitted"""
    orderedItems = request.POST.getlist('items')
    customerName = request.POST.get('customerName')
    customerPhone = request.POST.get('customerPhone')
    customerEmail = request.POST.get('customerEmail')
    specialInstructions = request.POST.get('specialInstructions')

    # Create a dictionary to lookup prices
    allItems = {
        'Chicken Parmesan': 15.99,
        'Steak and Cheese Sub': 11.49,
        'BLT Sandwich': 8.99,
        'Grilled Chicken Caesar Salad': 10.99,
        'Freddy\'s Supreme Pizza': 12.99,
        'Today\'s soup': 4.99,
        'Club Sandwich': 9.49,
        'Chefs Reccomendation': 12.99, 
        'The Humming': math.inf,  
        'The Taste of Yellow': 4.99,
        'The Exit': 0.00,
        'The Way Back': math.inf,
        'Meatloaf': 8.99,
        'Fish and Chips': 10.99,
        'The Wednesday Thing': 11.11,
        'Todays Fresh Catch': 14.44,
        'Your Usual': 14.99,
    }

    totalPrice = 0
    for i in orderedItems: 
        if i in allItems: 
            totalPrice += allItems[i]

    readyTimes = ["∞ minutes", "25:99 PM", "When you stop looking", "Soon™"]
    readyTime = random.choice(readyTimes)

    context = {
        'orderedItems': orderedItems,
        'customerName': customerName,
        'customerPhone': customerPhone,
        'customerEmail': customerEmail,
        'specialInstructions': specialInstructions,
        'totalPrice': totalPrice,
        'readyTime': readyTime,
    }
    
    return render(request, 'restaurant/notaconfirmation.html', context)

def level2(request):
    """Secret level 2 page"""
    return render(request, 'restaurant/level2.html')