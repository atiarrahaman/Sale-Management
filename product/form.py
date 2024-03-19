from django import forms
from .models import Product, Category
from .models import CartProduct

# Product Form
class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    qty = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    qr_image = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    image = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    status = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input custom-checkbox'}), required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'qty',
                  'category', 'qr_image', 'image', 'status']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name',]


class CartProductForm(forms.ModelForm):
    quantity = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    product = forms.ModelChoiceField(queryset=Product.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model=CartProduct
        fields = ['id', 'product','quantity']