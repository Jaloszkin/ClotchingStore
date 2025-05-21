from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Почта'
        })
    )
    phone = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12587467'
        })
    )
    message = forms.CharField(
        label="Ваше обращение",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Сообщение',
            'rows': 3
        })
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')