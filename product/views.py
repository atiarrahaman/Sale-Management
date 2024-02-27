from django.shortcuts import render
from django.http import HttpResponse
from .form import  ProductForm,CatagoryForm
from .models import Product,Catagory
# Create your views here.



def ProductView(request):
    return HttpResponse('product')