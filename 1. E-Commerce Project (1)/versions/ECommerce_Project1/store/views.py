from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView
)
from .models import Category, Brand, Spec, Item, ItemSpecValue

def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    specs = Spec.objects.all()
    item_spec_values = ItemSpecValue.objects.all()
    
    for item in items:
        item.discounted_price = item.discounted_price()
    
    context = {
        'items': items,
        'categories': categories,
        'specs': specs,
        'item_spec_values': item_spec_values,
        'brands': brands,
    }
    return render(request, 'store/home.html', context)


class ItemListView(ListView):
    model = Item
    template_name = 'store/home.html'
    context_object_name = 'items'
    ordering = ['-price']


class ItemDetailView(DetailView):
    model = Item
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title + " Details & Price"
        return context


def about(request):
    return render(request, 'store/about.html', {'title': 'About Us'})


def contact(request):
    return render(request, 'store/contact.html', {'title': 'Contact Us'})
