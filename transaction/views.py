from django.shortcuts import render
from django.http import HttpResponse
from .forms import ExpensiveForm,DepositeForm,WithdrawForm
from .models import Exprensive,Deposite,Withdraw
# Create your views here.



def Dashboard(request):
    return HttpResponse('Dashboard')