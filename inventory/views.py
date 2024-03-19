from django.shortcuts import render
from django.http import HttpResponse
from .models import Inventory
from .forms import InventoryForm
# Create your views here.



def InventoryView(request):
    return HttpResponse('Inventory')