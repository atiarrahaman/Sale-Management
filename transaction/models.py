from django.db import models
from inventory.models import Supplier
from django.contrib.auth.models import User
# Create your models here.


# Expense

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    def __str__(self):
        return f"Balance of {self.user.username}: {self.amount}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('sale', 'Sale'),
        ('payment', 'Payment'),
        ('expense', 'Expense'),
    )

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)


class Payment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField(auto_now_add=True)
    invoice = models.CharField(max_length=255, null=True, blank=True)
    paid = models.BooleanField(default=False)


class Expense(models.Model):
    EXPENSE_TYPES = (
        ('salary', 'Salary'),
        ('rent', 'Rent'),
        ('other', 'Other'),
    )

    type = models.CharField(max_length=10, choices=EXPENSE_TYPES)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
