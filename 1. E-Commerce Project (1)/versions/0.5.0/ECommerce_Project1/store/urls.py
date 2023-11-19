from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='store-home'),
    path('about-us/', views.about, name='store-about'),
    path('contact-us/', views.contact, name='store-contact')
]
