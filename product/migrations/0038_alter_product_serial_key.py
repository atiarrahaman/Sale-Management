# Generated by Django 4.2 on 2024-07-11 17:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0037_alter_product_serial_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='serial_key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]