# Generated by Django 4.2 on 2024-03-20 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_alter_product_category_alter_product_supplier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='buy_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sell_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]