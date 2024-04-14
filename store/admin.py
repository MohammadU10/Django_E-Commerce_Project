from django.contrib import admin
from .models import Category, Brand, Spec, Item, ItemSpecValue, Cart, CartItem

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Spec)
admin.site.register(Item)
admin.site.register(ItemSpecValue)
admin.site.register(Cart)
admin.site.register(CartItem)
