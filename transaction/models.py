from django.db import models
from product.models import Supplier
# Create your models here.


# Exprense

class Exprensive(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, blank=True, null=True)
    reason= models.CharField(max_length=500)
    invoice_picture=models.ImageField(upload_to='expensive', blank=True,null=True)
    timestamps = models.DateTimeField(auto_now_add=True, null=True)


class Deposite(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    reason= models.CharField(max_length=500)
    timestamps = models.DateTimeField(auto_now_add=True, null=True)


class Withdraw(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    reason= models.CharField(max_length=500)
    timestamps = models.DateTimeField(auto_now_add=True, null=True)


