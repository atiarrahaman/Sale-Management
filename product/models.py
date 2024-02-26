from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class Catagory(models.Model):
    name=models.CharField( max_length=150)

    def __str__(self):
        return self.name
    
# this is a products models 

class Product(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=50,unique=True)
    qty=models.IntegerField(blank=True,null=True)
    price=models.DecimalField( max_digits=5, decimal_places=2,blank=True,null=True)
    catagory=models.ForeignKey(Catagory, on_delete=models.CASCADE,blank=True,null=True)
    serial_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_iamge=models.ImageField( upload_to='qr_image', )
    image= models.ImageField(upload_to='product_image',blank=True,null=True )
    status=models.BooleanField()
    product_create_date=models.DateField( auto_now_add=True,blank=True,null=True)
    
    def __str__(self):
        return self.name
    


