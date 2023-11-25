from django.contrib import admin
from .models import Category, Spec, Item, ItemSpecs

admin.site.register(Category)
admin.site.register(Spec)
admin.site.register(Item)
admin.site.register(ItemSpecs)
