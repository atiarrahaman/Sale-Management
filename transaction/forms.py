from django import forms 
from .models import *

from django import forms
from .models import Payment, Expense


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['supplier', 'amount', 'invoice']


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['type', 'amount', 'description']
