# Generated by Django 4.2 on 2024-07-11 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0034_alter_product_serial_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='serial_key',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
