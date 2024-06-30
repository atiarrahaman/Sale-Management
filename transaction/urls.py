from django.urls import path
from . import views
urlpatterns = [
   
    path('transactions/', views.TransactionView.as_view(), name='transactions'),
    path('transaction-history/', views.TransactionHistoryView.as_view(), name='transaction_history'),

]
