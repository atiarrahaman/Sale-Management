# Generated by Django 4.2 on 2024-07-12 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0039_alter_product_serial_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
