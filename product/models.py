from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User
# Create your models here.


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    address=models.CharField(max_length=200)
    tax_id = models.PositiveIntegerField()
    phone = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)
    qty = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True)
    serial_key = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    qr_image = models.ImageField(upload_to='qr_image', blank=True, null=True)
    image = models.ImageField(upload_to='product_image', blank=True, null=True)
    is_active = models.BooleanField()
    timestamps = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    def __str__(self):
        return "Cart: " + str(self.cart.id) + "CartProduct: " + str(self.id)


class Order(models.Model):
    name = models.CharField(max_length=50)
    phone= models.CharField(max_length=50)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Order: " + str(self.order.id) + "OrderProduct: " + str(self.id)
