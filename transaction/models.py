from django.db import models
from inventory.models import Supplyer
# Create your models here.


# Exprense

class Exprensive(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    supplyer=models.ForeignKey(Supplyer, on_delete=models.CASCADE)
    reason= models.CharField(max_length=500)
    invoice_picture=models.ImageField(upload_to='expensive', blank=True,null=True)
    date=models.DateField( auto_now_add=True)


class Deposite(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    reason= models.CharField(max_length=500)
    date= models.DateField( auto_now_add=True)


class Withdraw(models.Model):
    amount=models.DecimalField( max_digits=12, decimal_places=2)
    reason= models.CharField(max_length=500)
    date= models.DateField( auto_now_add=True)


