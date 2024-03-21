from django.shortcuts import render, redirect
from .forms import ProductInventoryForm
from django.http import HttpResponse
from .models import Inventory,Category,Supplier
from django.views.generic import CreateView
from . forms import CategoryForm,SupplierForm
from product.models import Product
# Create your views here.

class InventoryView(CreateView):
    template_name = 'inventory.html'
    success_url = ''

    def get(self, request):
        product_form = ProductInventoryForm()
        supplier_form = SupplierForm()
        category_form = CategoryForm()
        categories = Category.objects.all()
        products = Product.objects.all()
        suppliers = Supplier.objects.all()
        inventory = Inventory.objects.all()

        return render(request, self.template_name, {
            'supplier_form': supplier_form,
            'category_form': category_form,
            'product_form': product_form,
            'categories': categories,
            'products': products,
            'suppliers': suppliers,
            'inventory': inventory,
        })

    def post(self, request):
        supplier_form = SupplierForm(request.POST)
        category_form = CategoryForm(request.POST)
        product_form = ProductInventoryForm(
            request.POST, request.FILES)

        if 'product_submit' in request.POST:
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.save()
                total = product.buy_price * product.qty
                Inventory.objects.create(
                    user=request.user, product=product, total=total)

                return redirect('inventory')
        elif 'supplier_submit' in request.POST:
            if supplier_form.is_valid():
                supplier_form.save()
                return redirect('inventory')
        elif 'category_submit' in request.POST:
            if category_form.is_valid():
                category_form.save()
                return redirect('inventory')

        return render(request, self.template_name, {
            'product_form': product_form,
            'supplier_form': supplier_form,
            'category_form': category_form,
        })
