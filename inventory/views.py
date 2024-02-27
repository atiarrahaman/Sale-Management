from django.shortcuts import render
from django.http import HttpResponse
from .models import Supplyer,Inventory
from .forms import SupplerForm,InventoryForm
# Create your views here.



def InventoryView(request):
    return HttpResponse('Inventory')