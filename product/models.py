from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User
from decimal import Decimal
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
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0)
    vat = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)

    def update_cart_total(self):
        cart_products = self.cartproduct_set.all()
        if cart_products.exists():
            subtotal_amount = sum(cp.subtotal for cp in cart_products)

            # Apply discount
            discount_amount = (Decimal(self.discount) /
                               Decimal(100)) * subtotal_amount
            subtotal_after_discount = subtotal_amount - discount_amount

            # Apply VAT
            vat_amount = (Decimal(self.vat) / Decimal(100)) * \
                subtotal_after_discount

            # Ensure total is not negative
            self.total = max(subtotal_after_discount +
                             vat_amount, Decimal('0.00'))
        else:
            self.total = Decimal('0.00')
            discount_amount = Decimal('0.00')
            vat_amount = Decimal('0.00')

        self.save()
        return discount_amount, vat_amount


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + "CartProduct: " + str(self.id)


class Order(models.Model):
    name = models.CharField(max_length=50,null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0.0)
    vat = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return "Order: " + str(self.order.id) + "OrderProduct: " + str(self.id)


class ReturnProduct(models.Model):
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
    return_quantity = models.IntegerField()
    return_reason = models.TextField(blank=True)
    is_damage = models.BooleanField(default=False)
    return_date = models.DateField(auto_now_add=True)

    def subtotal(self):
        return self.return_quantity * self.order_product.product.sell_price

    def __str__(self):
        return f"Return of {self.return_quantity} units of {self.order_product.product.name} from Order #{self.order_product.order.id}"

