from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Order


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    email = forms.EmailField(label='Почта', widget=forms.EmailInput(attrs={'placeholder': 'Почта'}))
    phone = forms.CharField(label='Номер телефона', max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+7 999 999 99 99'}))
    message = forms.CharField(label='Ваше обращение', widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Сообщение'}))

# forms.py
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address']

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get("address")
        zip_code = cleaned_data.get("zip_code")

        if not address and not zip_code:
            raise forms.ValidationError("Укажите либо адрес, либо почтовый индекс.")
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')