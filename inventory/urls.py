from django.urls import path
from . import views
urlpatterns = [
   
    path('inventory', views.InventoryView.as_view(), name='inventory'),
    path('all_product', views.AllProductView.as_view(), name='all_product'),
    path('add_new', views.NewProductView.as_view(), name='add_new'),
    path('manage-inventory/<int:pro_id>',
         views.ManageInventoryView.as_view(), name='manage-inventory'),

]
