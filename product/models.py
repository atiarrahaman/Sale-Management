from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User
# Create your models here.

UNIT =(
    ("PCS", "PCS"),
    ("KG","KG"),
    ("PACKET","PACKET"),
    ("LITTER","LITTER"),
)

class Product(models.Model):
    supplier = models.ForeignKey(
        'inventory.Supplier', on_delete=models.CASCADE, blank=True, null=True)
    inventory = models.ForeignKey(
        'inventory.Inventory', on_delete=models.CASCADE, related_name='inventory',null=True,blank=True)
    name = models.CharField(max_length=50, unique=True)
    qty = models.IntegerField(blank=True, null=True)
    unit=models.CharField(max_length=15,choices=UNIT,default='PCS')
    sell_price = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    buy_price = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    subtotal = models.IntegerField(null=True,blank=True,default=0)
    category = models.ForeignKey(
        'inventory.Category', on_delete=models.CASCADE, blank=True, null=True)
    serial_key = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    bar_code = models.CharField(max_length=50, null=True, blank=True, unique=True)

    image = models.ImageField(upload_to='product_image', blank=True, null=True)
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

    def update_cart_total(self):
        cart_products = self.cartproduct_set.all()
        total_amount = sum(cp.subtotal for cp in cart_products)
        self.total = total_amount
        self.save()


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
