from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from product.models import Product

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=200)
    phone = models.CharField(max_length=20,null=True,blank=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    unpaid_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)

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
    date = models.DateField(auto_now_add=True,null=True)


    def __str__(self) -> str:
        return "Inventory: " + str(self.id) + "To: " + str(self.total)


class ReturnToSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    return_quantity = models.IntegerField()
    return_reason = models.TextField(blank=True)
    return_date = models.DateField(auto_now_add=True)
    is_damage = models.BooleanField(default=False)

    def subtotal(self):
        return self.return_quantity * self.product.buy_price

    def __str__(self):
        return f"Return of {self.return_quantity} units of {self.product.name} to Supplier #{self.supplier.name}"
