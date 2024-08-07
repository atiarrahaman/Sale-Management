from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class ShopOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    trade_license_no = models.CharField(max_length=200)
    tex_id = models.CharField(max_length=200)
    shop_location = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    owner_photo = models.ImageField(default='default.png',
                                    upload_to='Owner_photo', null=True, blank=True)
    shop_photo = models.ImageField(default='default.png',
                              upload_to='shop_photo',null=True,blank=True)
    def __str__(self):
        return f'{self.shop_name}'


class Staff(models.Model):
    shop = models.ForeignKey(ShopOwner, on_delete=models.CASCADE,blank=True,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    nid_no = models.CharField(max_length=50,null=True,blank=True)
    education = models.CharField(max_length=50, null=True, blank=True)
    point = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    father_name = models.CharField(max_length=50,null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(default='default.png',
                              upload_to='profile_images')


    def __str__(self):
        return f'{self.user.username}'
