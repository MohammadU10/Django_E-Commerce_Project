from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView
)
from .models import Category, Spec, Item, ItemSpecs

def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    specs = Spec.objects.all()
    item_specs = ItemSpecs.objects.all()
    
    for item in items:
        item.display_spec = item_specs.filter(item=item, spec__name='Display').first()
        item.processor_spec = item_specs.filter(item=item, spec__name='Processor').first()
        item.ram_spec = item_specs.filter(item=item, spec__name='Memory (RAM)').first()
        item.discounted_price = item.discounted_price()
    
    context = {
        'items': items,
        'categories': categories,
        'specs': specs,
        'item_specs': item_specs
    }
    return render(request, 'store/home.html', context)


class ItemListView(ListView):
    model = Item
    template_name = 'store/home.html'
    context_object_name = 'items'
    ordering = ['-price']


class ItemDetailView(DetailView):
    model = Item


def about(request):
    return render(request, 'store/about.html', {'title': 'About Us'})


def contact(request):
    return render(request, 'store/contact.html', {'title': 'Contact Us'})
