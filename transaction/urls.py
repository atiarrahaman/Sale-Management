from django.urls import path
from . import views
urlpatterns = [
   
    path('transactions/', views.TransactionView.as_view(), name='transactions'),

    path('transaction_summary/', views.SummaryView.as_view(),
         name='transaction_summary'),

]
