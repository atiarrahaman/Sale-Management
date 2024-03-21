from django.urls import path
from . import views
urlpatterns = [
   
    path('inventory', views.InventoryView.as_view(), name='inventory'),

]
