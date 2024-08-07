# Generated by Django 4.2 on 2024-07-11 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_alter_cart_total_alter_order_total'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='bar_code',
            new_name='barcode',
        ),
        migrations.AddField(
            model_name='product',
            name='barcode_image',
            field=models.ImageField(blank=True, null=True, upload_to='product_barcodes'),
        ),
    ]
