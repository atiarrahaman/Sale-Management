from django.urls import path
from . import views
urlpatterns = [

    path('product', views.AddProductView.as_view(), name='product'),
    path('cart', views.CartView.as_view(), name='cart'),
    path('manage-cart/<int:cp_id>', views.ManageCartView.as_view(), name='manage-cart'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('all_order/', views.AllOrderView.as_view(), name='all_order'),

]
