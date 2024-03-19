from django.urls import path
from . import views
urlpatterns = [

    path('product', views.AddProductView.as_view(), name='product'),

]
