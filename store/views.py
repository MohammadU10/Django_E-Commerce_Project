from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    FormView
)
from .models import Category, Brand, Spec, Item, ItemSpecValue, Cart, CartItem, Review, Order, OrderItem
from .forms import CartUpdateQuantityForm, ReviewForm, ShipmentForm, PaymentSelectionForm
from .mixins import CartQuantityMixin, CartContextMixin
from django.db import transaction
from django.db.models import Avg, Count
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.http import HttpResponse, Http404
from azbankgateways import bankfactories, models as bank_models, default_settings as bank_settings
from azbankgateways.exceptions import AZBankGatewaysException
from decimal import Decimal
import logging

CustomUser = get_user_model()


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
        'brands': brands,
        'specs': specs,
        'item_spec_values': item_spec_values
    }
    return render(request, 'store/home.html', context)


class ItemListView(ListView):
    model = Item
    template_name = 'store/home.html'
    context_object_name = 'items'
    ordering = ['-price']


class ItemDetailView(CartQuantityMixin, DetailView):
    model = Item
    template_name = 'store/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        reviews_qs = item.review_set.all()
        
        context['title'] = f"{item.title} Details & Price"
        context['reviews'] = reviews_qs.select_related('author').order_by('-date_posted')

        # Average item score or rating
        avg_score = reviews_qs.aggregate(avg=Avg('rating'))['avg']
        context['average_score'] = round(avg_score or 0, 1)  # avoid None

        # Percentages per star rating for ratings progress bar
        total_reviews = reviews_qs.count()
        star_counts = (
            reviews_qs
            .values('rating')
            .annotate(count=Count('rating'))
        )

        # Create dictionary {star: percentage}
        percentages = {star: 0 for star in range(1, 6)}
        for entry in star_counts:
            star = entry['rating']
            count = entry['count']
            percentages[star] = round((count / total_reviews) * 100, 1) if total_reviews > 0 else 0

        context['rating_percentages'] = percentages
        context['total_reviews'] = total_reviews

        if 'form' not in context:
            from .views import ReviewCreateView
            context['form'] = ReviewCreateView.form_class()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        from .views import ReviewCreateView
        form = ReviewCreateView.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.item = self.object
            review.save()
            messages.success(request, "Your review has been added.")
            return redirect(self.request.path)  # stay on detail page
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.item = self.item
        return super().form_valid(form)


class CartItemListView(CartContextMixin, ListView):
    model = CartItem
    template_name = 'store/cart.html'
    context_object_name = 'cart_items'

    def get(self, request, *args, **kwargs):
        # Ensure a session exists for guests
        if not request.session.session_key:
            request.session.create()
        return super().get(request, *args, **kwargs)


class CartItemDeleteView(SuccessMessageMixin, DeleteView):
    model = CartItem
    success_message = "Item successfully Removed from cart."

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER') or reverse_lazy('cart')


class ShipmentView(LoginRequiredMixin, CartContextMixin, FormView):
    template_name = 'store/shipment.html'
    form_class = ShipmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        # Store shipping info in session
        self.request.session['shipping_address'] = form.cleaned_data['address']
        self.request.session['shipping_date'] = str(form.cleaned_data['date'])
        return redirect('payment')


class PaymentView(LoginRequiredMixin, CartContextMixin, FormView):
    template_name = 'store/payment.html'
    form_class = PaymentSelectionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Retrieve shipping info from session
        context['shipping_address'] = self.request.session.get('shipping_address')
        context['shipping_date'] = self.request.session.get('shipping_date')
        return context

    def form_valid(self, form):
        payment_method = form.cleaned_data['payment_method']
        context = self.get_context_data()
        cart_items = list(context.get('cart_items', []))

        with transaction.atomic():
            order = Order.objects.create(
                user=self.request.user,
                shipping_date=context['shipping_date'],
                total_cost=context['total_cost'],
                shipping_cost=context['shipping_cost'],
                grand_total=context['grand_total'],
                shipping_address=context['shipping_address']
            )
            # Create an OrderItem from each CartItem
            for ci in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=ci.item,
                    price=ci.item.price,
                    quantity=ci.quantity,
                )

        # Store only the order ID in session
        self.request.session['order_id'] = str(order.pk)

        return redirect('payment-start', order_id=order.pk)


@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart_url = reverse('cart')

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        sk = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=sk)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    message = format_html("Added {} to your cart. <a href=\"{}\">View Your Cart</a>.", item.title, cart_url)
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER') or cart_url)


@require_POST
def update_cart_item(request):
    cart_url = reverse('cart')
    form = CartUpdateQuantityForm(request.POST)
    if form.is_valid():
        ci = get_object_or_404(CartItem, id=form.cleaned_data['cart_item_id'])
        action = form.cleaned_data['action']
        if action == 'decrement':
            ci.quantity = max(ci.quantity - 1, 0)
            if ci.quantity == 0:
                ci.delete()
                messages.success(request, f"Removed {ci.item.title} from cart.")
                return redirect(request.META.get('HTTP_REFERER') or cart_url)
            ci.save()
        else:
            ci.quantity += 1
            ci.save()
        update_message = format_html("Updated quantity for {}. <a href=\"{}\">View Your Cart</a>.", ci.item.title, cart_url)
        messages.success(request, update_message)
    return redirect(request.META.get('HTTP_REFERER') or cart_url)


def payment_result(request, payment_id):
    # finalize order if needed, or show status
    return render(request, 'store/payment_result.html')


def start_payment(request, order_id):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    # Get your shop total in your app’s currency (align with AZ_IRANIAN_BANK_GATEWAYS['CURRENCY'])
    # If your totals are Decimal, cast to int for the gateway:
    amount = int(Decimal(order.grand_total))

    # Get user phone number, optional
    user_mobile_number = request.user.phone_number

    # Store order id in session for use in callback
    request.session['pay_order_id'] = str(order.pk)

    factory = bankfactories.BankFactory()
    try:
        # Use default gateway from settings; or pick explicitly, e.g. factory.create(bank_models.BankType.ZARINPAL)
        bank = factory.auto_create()
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(reverse('payment-callback'))  # after verify, it will redirect here

        # Optional: send mobile number if you have it (some providers use it)
        if request.user and request.user.phone_number:
            bank.set_mobile_number(str(user_mobile_number))

        # Persist request & get a DB record
        bank_record = bank.ready()

        # Finally redirect the user to the bank’s gateway
        return bank.redirect_gateway()

    except AZBankGatewaysException as e:
        logging.exception(e)
        # You might redirect to a “payment failed” page here
        raise e


def payment_callback(request):
    tracking_code = request.GET.get(bank_settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        raise Http404("Invalid callback")

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        raise Http404("Tracking code not found")

    # Retrieve the order (from session or your own linkage)
    order_id = request.session.get('pay_order_id')
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if bank_record.is_success:
        # Mark order paid, store receipt details, etc.
        if order:
            order.status = 'paid'
            order.save(update_fields=['status'])
        return HttpResponse("پرداخت با موفقیت انجام شد.")
    else:
        # Payment failed/cancelled/expired - show message or retry options
        return HttpResponse(format_html(("<p>پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.</p>"
            "<br><button><a href=\"{}\">بازگشت به فروشگاه.</a></button>"),
        reverse('store-home'))
        )


def about(request):
    return render(request, 'store/about.html', {'title': 'About Us'})


def contact(request):
    return render(request, 'store/contact.html', {'title': 'Contact Us'})
