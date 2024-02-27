from django import forms 

from .models import Supplyer,Inventory



# suppley form

class SupplerForm(forms.ModelForm):
    class Meta:
        model=Supplyer
        fields=['name','tax_id','phone']


#Inventory Form
        
class InventoryForm(forms.ModelForm):
    class Meta:
        model=Inventory
        fields=['name','price','qty','supplyer']