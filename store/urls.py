from django.urls import path
from .views import (
    ItemListView,
    ItemDetailView,
    CartItemListView,
    CartItemDeleteView,
    ShipmentView,
    PaymentView
)
from . import views

urlpatterns = [
    path('', ItemListView.as_view(), name='store-home'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('cart/', CartItemListView.as_view(), name='cart'),
    path("add-to-cart/<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path('cart/update-item/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete-item/<int:pk>', CartItemDeleteView.as_view(), name='delete_cart_item'),
    path('shipment/', ShipmentView.as_view(), name='shipment'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('checkout/<uuid:order_id>/start/', views.start_payment, name='payment-start'),
    path('payment/callback/', views.payment_callback, name='payment-callback'),
    path('payment-result/<uuid:payment_id>/', views.payment_result, name='payment-result'),
    path('about-us/', views.about, name='store-about'),
    path('contact-us/', views.contact, name='store-contact')
]
