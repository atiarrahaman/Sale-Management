from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Transaction, Payment
from .forms import PaymentForm, ExpenseForm
from inventory.models import Supplier
from django.db import transaction


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
