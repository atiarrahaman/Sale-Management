from django.shortcuts import render
from django.http import HttpResponse
from .models import Pos 
from .forms import PosForm
# Create your views here.


def PosView(request):
    return HttpResponse('Pos')