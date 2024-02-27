from django import forms 
from .models import Pos



class PosForm(forms.ModelForm):
    class Meta:
        model=Pos
        fields=['product','qty','discount']