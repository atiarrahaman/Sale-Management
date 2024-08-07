from django import forms
from .models import Product, CartProduct, Order, ReturnProduct,DamageProduct
from inventory .models import Category, Supplier,Brand
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
# Product Form
class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    
    qty = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    buy_price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    sell_price = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      empty_label='Select Category',
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(),
                                   empty_label='Select Brand',
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(),
                                      empty_label='Select Supplier',
                                      widget=forms.Select(attrs={'class': 'form-control'}))
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
                  'category', 'brand', 'supplier', 'image',]


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

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = ''
        self.fields['name'].widget.attrs.update({'placeholder': 'Customer Name'})
        
        self.fields['phone'].label = ''
        self.fields['phone'].widget.attrs.update({'placeholder': 'Phone Number'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('customer_name'),
            Field('phone'),
            # Add more fields as needed
        )


class ReturnProductForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['order_product', 'return_quantity', 'return_reason',
'is_damage'
        ]


class DamageProductForm(forms.ModelForm):
    class Meta:
        model = DamageProduct
        fields = ['damage_product', 'damage_quantity', 'is_returned']
        widgets = {
            'damage_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Quantity'
            }),
            'is_returned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['damage_product'].empty_label = 'Select Product'
        self.fields['damage_product'].widget.attrs.update({
            'class': 'form-control'
        })
