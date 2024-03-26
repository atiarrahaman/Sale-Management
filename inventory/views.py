from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Inventory, Category, Supplier
from django.views.generic import CreateView, TemplateView
from . forms import CategoryForm, SupplierForm
from product.models import Product
from django.db import transaction
from product .form import ProductForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib import messages
# Create your views here.


class InventoryView(TemplateView):
    template_name = 'inventory.html'

    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST)
        supplier_form = SupplierForm(request.POST)
        category_form = CategoryForm(request.POST)

        if product_form.is_valid():
            # Process product form submission
            product = product_form.save(commit=False)
            product.save()
            inventory_id = request.session.get("inventory_id")
            try:
                inventory_obj = Inventory.objects.get(id=inventory_id)
            except Inventory.DoesNotExist:
                inventory_obj = Inventory.objects.create(
                    user=request.user, total=0)
                request.session['inventory_id'] = inventory_obj.id

            product.inventory = inventory_obj
            product.save()
            inventory_obj.total += product.buy_price * product.qty
            inventory_obj.save()
            messages.success(
                request, f'{product.name} has been added to inventory')
        elif supplier_form.is_valid():
            supplier = supplier_form.save()
            messages.success(
                request, f'{supplier.name} has been added as a supplier')
        elif category_form.is_valid():
            category = category_form.save()
            messages.success(
                request, f'{category.name} has been added as a category')
        else:
            messages.error(
                request, 'Failed to add data. Please try again.')

        if 'add_inventory' in request.POST:
            del request.session['inventory_id']
            
        return redirect('inventory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_id = self.request.session.get("inventory_id")
        print("Inventory ID:", inventory_id)

        try:
            inventory_obj = Inventory.objects.get(id=inventory_id)
            inventory_products = inventory_obj.inventory.all()
            inventory_total = inventory_obj.total
        except Inventory.DoesNotExist:
            inventory_products = []
            inventory_total = 0
        product=Product.objects.all()
        inventories=Inventory.objects.all()
        inventory_data = {}

        for inventory in inventories:
            products = Product.objects.filter(inventory=inventory)           
            inventory_data[inventory] = products
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        context['product_form'] = ProductForm()
        context['supplier_form'] = SupplierForm()
        context['category_form'] = CategoryForm()
        context['inventory_products'] = inventory_products
        context['inventory_total'] = inventory_total
        context['categories'] = categories
        context['suppliers'] = suppliers
        context['inventories'] = inventories
        context['product'] = product
        context['inventory_data'] = inventory_data
        return context

