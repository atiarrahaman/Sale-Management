from django import forms 

from .models import Inventory,Category,Supplier

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


class ProductInventoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control'}))
    status = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input custom-checkbox'}), required=False)
    class Meta:
        model = Product
        fields = ['name', 'qty', 'buy_price', 'sell_price',
                  'category', 'image', 'qr_image', 'supplier', 'is_active']
        widgets={
            'name':forms.TextInput(
                attrs={'class': 'form-control'}),
            'qty': forms.TextInput(
        attrs={'class': 'form-control'}),
            'buy_price':forms.TextInput(
        attrs={'class': 'form-control'}),
            'sell_price':forms.TextInput(
        attrs={'class': 'form-control'}),
            
    'qr_image' : forms.TextInput(
        attrs={'class': 'form-control'}),
    'image' : forms.TextInput(
        attrs={'class': 'form-control'}),
    
        }

    def save(self, commit=True):
        product = super().save(commit=commit) 
        if commit:
            total = product.buy_price * product.qty
            Inventory.objects.create(
                user=self.instance.user,
                product=product,
                total=total
            )

        return product
