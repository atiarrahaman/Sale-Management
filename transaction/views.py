from django.db.models import Sum , OuterRef, Subquery
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
from transaction.models import Transaction,Payment,Expense,Balance
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




class SummaryView(View):
    template_name = 'transaction_summary.html'

    def get(self, request):
        user = request.user

        # Get the balance for the current user
        balance = get_object_or_404(Balance, user=user.shopowner)

        # Calculate total sales
        total_sales = Transaction.objects.filter(
            transaction_type='sale').aggregate(total_sales=Sum('amount'))

        # Calculate total expenses
        total_expenses = Transaction.objects.filter(
            transaction_type='expense').aggregate(total_expenses=Sum('amount'))

        # Calculate total payments
        total_payment = Transaction.objects.filter(
            transaction_type='payment').aggregate(total_payment=Sum('amount'))

        # Calculate profit
        profit = (total_sales['total_sales'] or 0) - \
            (total_expenses['total_expenses'] or 0)

        # Get sales and expenses transactions
        sales_transactions = Transaction.objects.filter(
            transaction_type='sale')
        expenses_transactions = Transaction.objects.filter(
            transaction_type='expense')

        # Get payment transactions and join with Payment model to get supplier name and invoice
        payment_transactions = Transaction.objects.filter(transaction_type='payment').annotate(
            supplier_name=Subquery(
                Payment.objects.filter(
                    amount=OuterRef('amount'),
                    date=OuterRef('date')
                ).values('supplier__name')[:1]
            ),
            invoice=Subquery(
                Payment.objects.filter(
                    amount=OuterRef('amount'),
                    date=OuterRef('date')
                ).values('invoice')[:1]
            )
        )

        context = {
            'balance': balance.amount,
            'total_sales': total_sales['total_sales'] or 0,
            'total_expenses': total_expenses['total_expenses'] or 0,
            'profit': profit,
            'sales_transactions': sales_transactions,
            'expenses_transactions': expenses_transactions,
            'total_payment': total_payment['total_payment'] or 0,
            'payment_transactions': payment_transactions,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user

        # Get the balance for the current user
        balance = get_object_or_404(Balance, user=user.shopowner)

        # Get start and end date from form
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        supplier = request.POST.get('supplier')
        amount = request.POST.get('amount')

        filters = Q()
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filters &= Q(date__gte=start_date, date__lte=end_date)

        # Calculate total sales
        total_sales = Transaction.objects.filter(
            transaction_type='sale').filter(filters).aggregate(total_sales=Sum('amount'))

        # Calculate total expenses
        total_expenses = Transaction.objects.filter(
            transaction_type='expense').filter(filters).aggregate(total_expenses=Sum('amount'))

        # Calculate total payments
        total_payment = Transaction.objects.filter(
            transaction_type='payment').filter(filters).aggregate(total_payment=Sum('amount'))

        # Calculate profit
        profit = (total_sales['total_sales'] or 0) - \
            (total_expenses['total_expenses'] or 0)

        # Get sales and expenses transactions within date range
        sales_transactions = Transaction.objects.filter(
            transaction_type='sale').filter(filters)
        expenses_transactions = Transaction.objects.filter(
            transaction_type='expense').filter(filters)

        # Get payment transactions within date range and join with Payment model to get supplier name and invoice
        payment_transactions = Transaction.objects.filter(transaction_type='payment').filter(filters).annotate(
            supplier_name=Subquery(
                Payment.objects.filter(
                    amount=OuterRef('amount'),
                    date=OuterRef('date')
                ).values('supplier__name')[:1]
            ),
            invoice=Subquery(
                Payment.objects.filter(
                    amount=OuterRef('amount'),
                    date=OuterRef('date')
                ).values('invoice')[:1]
            )
        )

        context = {
            'balance': balance.amount,
            'total_sales': total_sales['total_sales'] or 0,
            'total_expenses': total_expenses['total_expenses'] or 0,
            'profit': profit,
            'sales_transactions': sales_transactions,
            'expenses_transactions': expenses_transactions,
            'total_payment': total_payment['total_payment'] or 0,
            'payment_transactions': payment_transactions,
        }

        return render(request, self.template_name, context)
