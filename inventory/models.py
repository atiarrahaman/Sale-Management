from django.db import models
from django.contrib.auth.models import User
from product.models import Product
# Create your models here.
# Supllyer Models

class Supplyer(models.Model):
    name=models.CharField( max_length=150)
    tax_id=models.PositiveIntegerField()
    phone=models.PositiveIntegerField(blank=True,null=True)
    def __str__(self) -> str:
        return self.name

#Inventory models
class Inventory(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.ForeignKey(Product, on_delete=models.CASCADE)
    price=models.DecimalField( max_digits=5, decimal_places=2)
    qty=models.PositiveIntegerField()
    supplyer=models.ForeignKey(Supplyer, on_delete=models.CASCADE)
    inventroy_add_date=models.DateField( auto_now_add=True,blank=True,null=True)


    def __str__(self) -> str:
        return self.name.name