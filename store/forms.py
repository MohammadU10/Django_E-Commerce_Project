from django import forms
from .models import Review
import datetime

class CartUpdateQuantityForm(forms.Form):
    cart_item_id = forms.IntegerField(widget=forms.HiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)  # 'increment' or 'decrement'


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput())
    
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']


class ShipmentForm(forms.Form):
    address = forms.ChoiceField(
        label = "Shipping Address",
        widget = forms.RadioSelect,
        choices = []
    )
    date = forms.DateField(
        label = "Preferred Ship Date",
        widget = forms.SelectDateWidget()
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            addresses = user.addresses.all()
            self.fields['address'].choices = [
                (addr.id, str(addr)) for addr in addresses
            ]

        # Calculate next 5 selectable dates (excluding Fridays and Saturdays)
        selectable = []
        today = datetime.date.today()
        days_checked = 0
        current = today
        while len(selectable) < 5 and days_checked < 14:  # limit loop for safety
            current += datetime.timedelta(days=1)
            days_checked += 1
            if current.weekday() not in (4, 5):
                selectable.append(current)

        self.fields['date'].choices = [(d, d.strftime("%A, %b %d, %Y")) for d in selectable]
        self.fields['date'].widget = forms.Select(choices=self.fields['date'].choices)
    
    def clean_date(self):
        selected = self.cleaned_data.get('date')
        valid = [choice[0] for choice in self.fields['date'].choices]
        if selected not in valid:
            raise forms.ValidationError("Please choose a valid shipping date.")
        return selected


class PaymentSelectionForm(forms.Form):
    PAYMENT_CHOICES = [
        ('payu', 'PayU'),
    ]

    payment_method = forms.ChoiceField(
        label="Select Payment Method",
        widget=forms.RadioSelect,
        choices=PAYMENT_CHOICES,
        initial='ZarinPal | زرین پال',
    )
