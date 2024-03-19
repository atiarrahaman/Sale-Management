from django import forms 

from .models import Inventory


#Inventory Form
        
class InventoryForm(forms.ModelForm):
    class Meta:
        model=Inventory
        fields=['name','price','qty']