from django import forms
from .models import Product,CartProduct,Order
from inventory .models import Category, Supplier
# Product Form
class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    qty = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    sell_price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    qr_image = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    image = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    status = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input custom-checkbox'}), required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'sell_price', 'qty',
                  'category', 'qr_image', 'image', 'status','supplier']



class CartProductForm(forms.ModelForm):
    quantity = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    product = forms.ModelChoiceField(queryset=Product.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model=CartProduct
        fields = ['id', 'product','quantity']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone']
