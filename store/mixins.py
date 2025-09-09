from django.views.generic.base import ContextMixin
from .models import Cart, CartItem

class CartQuantityMixin(ContextMixin):
    def get_cart(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user).first()
        sk = self.request.session.session_key or self.request.session.create()
        return Cart.objects.filter(session_key=sk).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = context.get('items')
        obj = context.get('item') or context.get('object')
        iterable = items if items is not None else ([obj] if obj else [])

        cart = self.get_cart()
        ci_map = {}
        if cart:
            cis = CartItem.objects.filter(cart=cart, item_id__in=[i.id for i in iterable])
            ci_map = {ci.item_id: ci for ci in cis}

        for item in iterable:
            ci = ci_map.get(item.id)
            item.cart_quantity = ci.quantity if ci else 0
            item.cart_item_id = ci.id if ci else None

        return context


class CartContextMixin:
    def get_queryset(self):
        request = self.request
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            sk = request.session.session_key
            cart = Cart.objects.filter(session_key=sk).first()
        if cart:
            return cart.cartitem_set.select_related('item')
        else:
            return CartItem.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        items_with_totals = [(ci, ci.quantity * ci.item.price) for ci in cart_items]
        total_items = sum(ci.quantity for ci in cart_items)
        total_cost = sum(subtotal for _, subtotal in items_with_totals)
        shipping_cost = total_items * 5
        grand_total = total_cost + shipping_cost

        context.update({
            'cart_items': cart_items,
            'items_with_totals': items_with_totals,
            'total_items': total_items,
            'total_cost': total_cost,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total
        })
        return context
