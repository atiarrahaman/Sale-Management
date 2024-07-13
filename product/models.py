from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import User
from decimal import Decimal
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from core.models import ShopOwner
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
    brand = models.ForeignKey(
        'inventory.Brand', on_delete=models.CASCADE, blank=True, null=True)
    serial_key = models.CharField(
        max_length=13, editable=False, unique=True)
    barcode = models.CharField(max_length=50, null=True, blank=True, unique=True)
    barcode_image = models.ImageField(
        upload_to='product_barcodes', blank=True, null=True)

    image = models.ImageField(upload_to='product_image', blank=True, null=True)
    timestamps = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    def generate_serial_key(self):
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        return f"{current_year}{current_month:02d}{self.id:05d}"

    def save(self, *args, **kwargs):
        if not self.serial_key:
            super().save(*args, **kwargs)  # Save to generate ID first
            self.serial_key = self.generate_serial_key()
            super().save(*args, **kwargs)  # Save again to update serial_key
        else:
            super().save(*args, **kwargs)
        print(self.serial_key)




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
    invoice = models.CharField(
        max_length=20, unique=True, blank=True, null=True)

    def generate_invoice(self):

        shop_owner = ShopOwner.objects.first()
        shop_name_initials = ''.join([word[0].upper()
                                     for word in shop_owner.shop_name.split()])

        last_order = Order.objects.filter(
            invoice__startswith=shop_name_initials).order_by('id').last()
        if last_order:
            last_invoice_number = int(last_order.invoice.split('-')[-1])
            new_invoice_number = last_invoice_number + 1
        else:
            new_invoice_number = 1

        return f'{shop_name_initials}-{new_invoice_number:04d}'

    def save(self, *args, **kwargs):
        if not self.invoice:
            self.invoice = self.generate_invoice()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order: {self.id}"


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


class DamageProduct(models.Model):
    damage_product=models.ForeignKey(Product,on_delete=models.CASCADE)
    damage_quantity = models.IntegerField()
    is_returned = models.BooleanField(default=False)

    def subtotal(self):
        return self.damage_quantity * self.damage_product.buy_price
    
    def __str__(self):
        return f"Damage {self.id}"
