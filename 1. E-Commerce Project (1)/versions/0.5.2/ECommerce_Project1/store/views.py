from django.shortcuts import render
from .models import Item

def home(request):
    items = Item.objects.all()
    
    for item in items:
        item.discounted_price = item.discounted_price()
    
    context = {
        'items': items,
    }
    return render(request, 'store/home.html', context)


def about(request):
    return render(request, 'store/about.html', {'title': 'About Us'})


def contact(request):
    return render(request, 'store/contact.html', {'title': 'Contact Us'})
