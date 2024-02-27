from django import forms 
from .models import Deposite,Exprensive,Withdraw



class ExpensiveForm(forms.ModelForm):
    class Meta:
        model=Exprensive
        fields=['amount','supplyer','reason','invoice_picture']



class DepositeForm(forms.ModelForm):
    class Meta:
        model=Deposite
        fields=['amount','reason']



class WithdrawForm(forms.ModelForm):
    class Meta:
        model=Withdraw
        fields=['amount','reason']