from django.urls import path
from .views import (
    ItemListView,
    ItemDetailView
)
from . import views

urlpatterns = [
    path('', ItemListView.as_view(), name='store-home'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('about-us/', views.about, name='store-about'),
    path('contact-us/', views.contact, name='store-contact')
]
