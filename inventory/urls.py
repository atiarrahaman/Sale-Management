from django.urls import path
from . import views
urlpatterns = [
   
    path('inventory', views.InventoryView.as_view(), name='inventory'),
    path('all_product', views.AllProductView.as_view(), name='all_product'),
    path('add_product', views.NewProductView.as_view(), name='add_product'),
    path('add_category', views.CategoryView.as_view(), name='add_category'),
    path('add_supplier', views.SupplierView.as_view(), name='add_supplier'),
    path('delete_supplier/<int:pk>/',
         views.SupplierDeleteView.as_view(), name='delete_supplier'),
    path('manage-inventory/<int:pro_id>',
         views.ManageInventoryView.as_view(), name='manage-inventory'),
    path('return-to-supplier/', views.ReturnToSupplierView.as_view(),
         name='return_to_supplier'),
    path('return-supplier-products/', views.ReturnToSupplierProductListView.as_view(),
         name='return-supplier-products'),

]
