# Generated by Django 4.2 on 2024-07-11 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_alter_cart_total_alter_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]