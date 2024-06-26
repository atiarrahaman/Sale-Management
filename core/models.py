from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    education = models.CharField(max_length=50, null=True, blank=True)
    point = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    father_name = models.CharField(max_length=50,null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(default='default.png',
                              upload_to='profile_images')

    def __str__(self):
        return f'{self.user.username}'
