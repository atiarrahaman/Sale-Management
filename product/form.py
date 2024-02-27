from django import forms
from .models import Product,Catagory



#Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','price','qty','catagory','qr_iamge','image','status']


#Catagory Form


class CatagoryForm(forms.ModelForm):
    class Meta:
        model=Catagory
        fields=['name',]