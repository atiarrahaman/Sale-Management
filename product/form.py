from django import forms
from .models import Product, CartProduct, Order, ReturnProduct
from inventory .models import Category, Supplier
# Product Form
class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    bar_code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    qty = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    buy_price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    sell_price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    image= forms.FileInput(attrs={'class': 'form-control'}),
    UNIT_CHOICES = (
        ("PCS","PCS"),
        ("KG","KG"),
        ("PACKET","PACKET"),
        ("LITTER","LITTER"),
    )
    unit = forms.ChoiceField(choices=UNIT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


    class Meta:
        model = Product
        fields = ['id','name', 'qty', 'unit', 'buy_price', 'sell_price',
                  'category', 'supplier', 'image', 'bar_code']


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


class ReturnProductForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['order_product', 'return_quantity', 'return_reason',
'is_damage'
        ]
