from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Address
from django.forms.models import inlineformset_factory


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'phone_number']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


DEFAULT_ATTRS = {'data-lpignore': 'true'}

class PersonalInfoUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone_number', 'email']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('user',)

AddressFormSet = inlineformset_factory(
    parent_model=get_user_model(),
    model=Address,
    form=AddressForm,
    extra=1,              # Shows one blank form for adding new
    can_delete=True
)
