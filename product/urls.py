from django.urls import path
from . import views
urlpatterns = [

    path('product', views.AddProductView.as_view(), name='product'),
    path('cart', views.CartView.as_view(), name='cart'),
    path('manage-cart/<int:cp_id>', views.ManageCartView.as_view(), name='manage-cart'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('all_order/', views.AllOrderView.as_view(), name='all_order'),
    path('return_product/', views.return_product, name='return_product'),
    path('return-products/', views.ReturnProductListView.as_view(),
         name='return_products'),
    path('damage-products/', views.DamageProductListView.as_view(),
         name='damage_products'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('update-cart-settings/', views.UpdateCartSettingsView.as_view(),
         name='update-cart-settings'),
    

]
