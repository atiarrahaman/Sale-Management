# Generated by Django 4.2 on 2024-06-26 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_product_subtotal_product_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_active',
        ),
        migrations.AddField(
            model_name='product',
            name='bar_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('PCS', 'PCS'), ('KG', 'KG'), ('PACKET', 'PACKET'), ('LITTER', 'LITTER')], default='PCS', max_length=15),
        ),
    ]
