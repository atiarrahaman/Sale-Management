# Generated by Django 4.2 on 2024-07-08 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_shopowner_role_remove_staff_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopowner',
            name='owner_photo',
            field=models.ImageField(blank=True, default='default.png', null=True, upload_to='Owner_photo'),
        ),
        migrations.AddField(
            model_name='shopowner',
            name='shop_photo',
            field=models.ImageField(blank=True, default='default.png', null=True, upload_to='shop_photo'),
        ),
    ]
