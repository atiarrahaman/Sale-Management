from django import forms 

from .models import Inventory, Category, Supplier, ReturnToSupplier,Brand

from product.models import Product


class QuantityForm(forms.Form):
   product = forms.ModelChoiceField(
       queryset=Product.objects.all(),
       empty_label='Select Product',
       label='',
       widget=forms.Select(attrs={
           'class': 'form-control',
       })
   )
   quantity = forms.IntegerField(
       label='',
       widget=forms.NumberInput(attrs={
           'class': 'form-control',
           'placeholder': 'Enter Quantity'
       })
   )

class BrandForm(forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    class Meta:
        model = Brand
        fields = ['name',]

class CategoryForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    class Meta:
        model = Category
        fields = ['name',]

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'tax_id', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Supplier Name'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
        self.fields['tax_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tax ID'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Supplier Address'
        })


class ReturnToSupplierForm(forms.ModelForm):

    class Meta:
        model = ReturnToSupplier
        fields = ['product','supplier', 'return_quantity', 'return_reason'
                
                  ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = 'Select Product'
        self.fields['product'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Select Product'
        })
        self.fields['supplier'].empty_label = 'Select Supplier'
        self.fields['supplier'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Select Supplier'
        })
        self.fields['return_quantity'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Return Quantity'
        })
        self.fields['return_reason'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Return Reason',
            'maxlength': '255'
        })
