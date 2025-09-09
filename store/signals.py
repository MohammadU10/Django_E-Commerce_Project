from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import Cart, CartItem

@receiver(user_logged_in)
def merge_carts(sender, user, request, **kwargs):
    sk = request.session.session_key
    if not sk:
        return
    try:
        guest_cart = Cart.objects.get(session_key=sk)
    except Cart.DoesNotExist:
        return
    user_cart, _ = Cart.objects.get_or_create(user=user)
    for ci in guest_cart.cartitem_set.all():
        uc, created = CartItem.objects.get_or_create(cart=user_cart, item=ci.item)
        if not created:
            uc.quantity += ci.quantity
            uc.save()
    guest_cart.delete()
