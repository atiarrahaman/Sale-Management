# Generated by Django 5.0.2 on 2024-02-26 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_inventory_inventroy_add_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='qty',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
