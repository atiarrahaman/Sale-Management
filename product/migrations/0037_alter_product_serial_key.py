# Generated by Django 4.2 on 2024-07-11 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0036_alter_product_serial_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='serial_key',
            field=models.CharField(editable=False, max_length=11, unique=True),
        ),
    ]
