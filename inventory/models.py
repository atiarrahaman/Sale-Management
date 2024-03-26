from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=200)
    phone = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
#Inventory models
class Inventory(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    timestamps = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self) -> str:
        return "Inventory: " + str(self.id) + "To: " + str(self.total)
