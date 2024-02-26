from django.db import models
from product.models import Product
# Create your models here.


#Client Model

class Client(models.Model):
    name=models.CharField( max_length=150)
    tax_id=models.PositiveIntegerField()
    phone=models.PositiveIntegerField(blank=True,null=True)

#Pos Model
    
class Pos(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    qty=models.PositiveIntegerField(default=1)
    discount=models.DecimalField( max_digits=5, decimal_places=2)

#Payment Type
class Payment_type(models.Model):
    payment_type = models.CharField(max_length=200)


#Checkout
class Checkout(models.Model):
    pos=models.ForeignKey(Pos,on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    order_date=models.DateField( auto_now_add=True)
    qty=models.PositiveIntegerField(default=1)
    payment_type=models.ForeignKey(Payment_type, on_delete=models.CASCADE,blank=True,null=True)