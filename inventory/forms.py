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
        fields = '__all__'

        widgets={
            'name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(
                attrs={'class': 'form-control'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control'}),
        }


# class ReturnProductForm(forms.ModelForm):
#     class Meta:
#         model = ReturnToSupplier
#         fields = ['order_product', 'return_quantity', 'return_reason',
#                   'is_damage'
#                   ]
