# Generated by Django 4.2 on 2024-03-20 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_rename_name_inventory_product_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('address', models.CharField(max_length=200)),
                ('tax_id', models.PositiveIntegerField()),
                ('phone', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='product',
            new_name='product_name',
        ),
    ]
