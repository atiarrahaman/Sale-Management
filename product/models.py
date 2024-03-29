from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User
# Create your models here.


class Product(models.Model):
    supplier = models.ForeignKey(
        'inventory.Supplier', on_delete=models.CASCADE, blank=True, null=True)
    inventory = models.ForeignKey(
        'inventory.Inventory', on_delete=models.CASCADE, related_name='inventory',null=True,blank=True)
    name = models.CharField(max_length=50, unique=True)
    qty = models.IntegerField(blank=True, null=True)
    sell_price = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    buy_price = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    category = models.ForeignKey(
        'inventory.Category', on_delete=models.CASCADE, blank=True, null=True)
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
    phone = models.CharField(max_length=50)
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
