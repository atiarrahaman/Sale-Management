from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Staff
from django.contrib.auth.models import User


class StaffCreationForm(UserCreationForm):
    address = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=50)
    image = forms.ImageField()
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1',
                  'password2', 'address', 'phone', 'image')
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'image': forms.TextInput(
                attrs={'class': 'form-control'}),

        }
