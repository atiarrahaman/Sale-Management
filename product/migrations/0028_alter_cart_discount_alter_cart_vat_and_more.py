# Generated by Django 4.2 on 2024-07-11 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0027_cart_discount_cart_vat_order_discount_order_vat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='discount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cart',
            name='vat',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.IntegerField(default=0.0),
        ),
        migrations.AlterField(
            model_name='order',
            name='vat',
            field=models.IntegerField(default=15),
        ),
    ]
