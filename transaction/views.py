from django.db.models import Sum
from django.views.generic import TemplateView
from django.shortcuts import redirect,render,get_object_or_404
from django.contrib import messages
from .models import Transaction, Payment
from .forms import PaymentForm, ExpenseForm
from inventory.models import Supplier
from django.db import transaction
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
from product.models import Product, Order, OrderProduct
from transaction.models import Transaction,Payment,Expense
from django.views import View
from django.db.models import Q
from datetime import datetime
class TransactionView(TemplateView):
    template_name = 'transactions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all transactions
        context['transactions'] = Transaction.objects.all()

        # Fetch all unpaid suppliers
        context['suppliers'] = Supplier.objects.filter(unpaid_amount__gt=0)

        # Initialize forms
        context['payment_form'] = PaymentForm()
        context['expense_form'] = ExpenseForm()

        return context

    def post(self, request, *args, **kwargs):
        print("POST data:", request.POST)  # Debug print

        if 'payment_submit' in request.POST:
            payment_form = PaymentForm(request.POST)
            print("Payment Form is valid:",
                  payment_form.is_valid())  # Debug print

            if not payment_form.is_valid():
                print("Payment Form errors:", payment_form.errors)  # Debug print
                messages.error(request, 'Payment form is not valid.')
                return self.render_to_response(self.get_context_data())

            amount = payment_form.cleaned_data['amount']
            invoice = payment_form.cleaned_data['invoice']
            supplier = request.POST.get('supplier')
            print("Supplier ID:", supplier)  # Debug print
            print("Amount:", amount)  # Debug print
            print("Invoice:", invoice)  # Debug print

            try:
                supplier = get_object_or_404(Supplier, pk=supplier)
            except Supplier.DoesNotExist:
                messages.error(request, 'Supplier not found.')
                return redirect('transactions')

            # Ensure payment amount does not exceed unpaid amount
            if amount > supplier.unpaid_amount:
                messages.error(
                    request, 'Payment amount exceeds unpaid amount.')
                return redirect('transactions')

            try:
                with transaction.atomic():
                    # Update supplier's unpaid amount
                    supplier.unpaid_amount -= amount
                    supplier.save()
                    print("Supplier unpaid amount updated.")  # Debug print

                    # Create Payment record
                    Payment.objects.create(
                        supplier=supplier,
                        amount=amount,
                        invoice=invoice,
                        paid=True
                    )
                    print("Payment record created.")  # Debug print

                    # Record Transaction
                    Transaction.objects.create(
                        transaction_type='payment',
                        amount=amount,
                        balance_after_transaction=supplier.unpaid_amount,
                        description=f"Payment to {supplier.name} for invoice {invoice}"
                    )
                    print("Transaction recorded.")  # Debug print

                messages.success(request, 'Payment recorded successfully.')
                return redirect('transactions')

            except Exception as e:
                print("Error during transaction:", e)  # Debug print
                messages.error(request, 'Error recording payment.')
                return redirect('transactions')

        elif 'expense_submit' in request.POST:
            expense_form = ExpenseForm(request.POST)
            print("Expense Form is valid:",
                  expense_form.is_valid())  # Debug print

            if not expense_form.is_valid():
                print("Expense Form errors:", expense_form.errors)  # Debug print
                messages.error(request, 'Expense form is not valid.')
                return self.render_to_response(self.get_context_data())

            expense_form.save()

            # Record Transaction for the expense
            amount = expense_form.cleaned_data['amount']
            description = expense_form.cleaned_data['description']
            Transaction.objects.create(
                transaction_type='expense',
                amount=amount,
                balance_after_transaction=0,  # Update this according to your logic
                description=description
            )

            messages.success(request, 'Expense recorded successfully.')
            return redirect('transactions')

        # If neither form is valid or if form submission failed, render the template again
        return self.render_to_response(self.get_context_data())


# class TransactionHistoryView(View):
#     template_name = 'transaction_history.html'

#     def get(self, request):
#         # Fetch and filter data based on request parameters
#         transaction_type = request.GET.get('transaction_type', '')
#         supplier_name = request.GET.get('supplier_name', '')
#         amount = request.GET.get('amount', '')
#         start_date_str = request.GET.get('start_date', '')
#         end_date_str = request.GET.get('end_date', '')

#         filters = Q()
#         if transaction_type:
#             filters &= Q(transaction_type=transaction_type)
#         if amount:
#             filters &= Q(amount=amount)
#         if start_date_str and end_date_str:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#             filters &= Q(date__range=(start_date, end_date))

#         transactions = Transaction.objects.filter(filters)

#         # Filter by supplier name if transaction type is 'payment'
#         if transaction_type == 'payment' and supplier_name:
#             payments = Payment.objects.filter(
#                 supplier__name__icontains=supplier_name)
#             payment_ids = payments.values_list('id', flat=True)
#             transactions = transactions.filter(id__in=payment_ids)

#         # Process each transaction to include supplier name and invoice if payment
#         for transaction in transactions:
#             if transaction.transaction_type == 'payment':
#                 payment = Payment.objects.filter(
#                     amount=transaction.amount, date=transaction.date).first()
#                 transaction.supplier_name = payment.supplier.name if payment else ''
#                 transaction.invoice = payment.invoice if payment else ''
#             else:
#                 transaction.supplier_name = ''
#                 transaction.invoice = ''

#         context = {
#             'transactions': transactions,
#             'transaction_type': transaction_type,
#             'supplier_name': supplier_name,
#             'amount': amount,
#             'start_date': start_date_str,
#             'end_date': end_date_str,
#         }

#         return render(request, self.template_name, context)


class TransactionHistoryView(View):
    template_name = 'transaction_history.html'

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d%m%Y').date()
        except ValueError:
            return None

    def get(self, request):
        # Fetch and filter data based on request parameters
        transaction_type = request.GET.get('transaction_type', '')
        supplier_name = request.GET.get('supplier_name', '')
        amount = request.GET.get('amount', '')
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        filters = Q()
        if transaction_type:
            filters &= Q(transaction_type=transaction_type)
        if amount:
            filters &= Q(amount=amount)

        start_date = self.parse_date(start_date_str)
        end_date = self.parse_date(end_date_str)

        if start_date and end_date:
            filters &= Q(date__range=(start_date, end_date))

        transactions = Transaction.objects.filter(filters)

        # Filter by supplier name if transaction type is 'payment'
        if transaction_type == 'payment' and supplier_name:
            payments = Payment.objects.filter(
                supplier__name__icontains=supplier_name)
            payment_ids = payments.values_list('id', flat=True)
            transactions = transactions.filter(id__in=payment_ids)

        # Calculate total order revenue

        orders=Order.objects.all()
        orderProducts = OrderProduct.objects.all()
        total_sell = sum(order.total for order in orders)
        total_order_product_cost = sum(
            orderProduct.product.buy_price for orderProduct in orderProducts)
        # print(total_order_product_cost)
        

        # Calculate total expenses
        total_expenses = sum(
            transaction.amount for transaction in transactions if transaction.transaction_type == 'expense')
        total_sell_price = total_sell-total_order_product_cost
        # Calculate total cost of order products
        
        revenue = total_sell_price - total_expenses


        context = {
            'transactions': transactions,
            'transaction_type': transaction_type,
            'supplier_name': supplier_name,
            'amount': amount,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'revenue': revenue,
            'total_sell_price':total_sell_price,
            'total_expenses': total_expenses

        }

        return render(request, self.template_name, context)
