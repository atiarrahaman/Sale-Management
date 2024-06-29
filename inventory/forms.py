from django import forms 

from .models import Inventory, Category, Supplier, ReturnToSupplier

from product.models import Product


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
