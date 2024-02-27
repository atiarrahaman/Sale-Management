from django.urls import path
from . import views
urlpatterns = [
   
    path('inventory',views.InventoryView,name='inventory'),

]
