# Generated by Django 4.2 on 2024-03-19 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_supplier_rename_status_product_is_active_and_more'),
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deposite',
            name='date',
        ),
        migrations.RemoveField(
            model_name='exprensive',
            name='date',
        ),
        migrations.RemoveField(
            model_name='exprensive',
            name='supplyer',
        ),
        migrations.RemoveField(
            model_name='withdraw',
            name='date',
        ),
        migrations.AddField(
            model_name='deposite',
            name='timestamps',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='exprensive',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.supplier'),
        ),
        migrations.AddField(
            model_name='exprensive',
            name='timestamps',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='withdraw',
            name='timestamps',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]