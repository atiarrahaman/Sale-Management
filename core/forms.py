from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Staff
from django.contrib.auth.models import User


class StaffCreationForm(UserCreationForm):
    address = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=50)
    image = forms.ImageField()
    education = forms.CharField(max_length=50)
    point = forms.DecimalField(max_digits=12, decimal_places=2)
    father_name = forms.CharField(max_length=50)
    mother_name = forms.CharField(max_length=50)
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    education = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    point = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    father_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    mother_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1',
                  'password2', 'address', 'phone', 'image', 'education', 'point', 'father_name', 'mother_name')
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


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ('phone', 'image', 'address','education','point')
        widgets = {
            
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'point': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
