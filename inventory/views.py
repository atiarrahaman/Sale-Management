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
from datetime import datetime
from django.views import View
from .filters import ProductFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.


class NewProductView(TemplateView):
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
        return redirect('add_new')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_id = self.request.session.get("inventory_id")

        try:
            inventory_obj = Inventory.objects.get(id=inventory_id)
            print("Inventory Object:", inventory_obj)
            inventory_products = inventory_obj.inventory.all()
            print("Inventory Products:", inventory_products)
            inventory_total = inventory_obj.total
        except Inventory.DoesNotExist:
            inventory_products = []
            inventory_total = 0
        print(inventory_products)
        context['product_form'] = ProductForm()
        context['supplier_form'] = SupplierForm()
        context['category_form'] = CategoryForm()
        context['inventory_products'] = inventory_products
        context['inventory_total'] = inventory_total

        return context


class AllProductView(View):
    template_name = 'all_product.html'

    def get(self, request, *args, **kwargs):
        all_product = Product.objects.all()
        myfilter = ProductFilter(request.GET, queryset=all_product)
        product = myfilter.qs
        context = {
            'myfilter': myfilter,
            'product': product
        }
        return render(request, self.template_name, context)


class InventoryView(TemplateView):
    template_name = 'manage_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = Inventory.objects.filter(
                timestamps__date__gte=start_date, timestamps__date__lte=end_date)
        else:
            queryset = Inventory.objects.all()

        inventory_data = {}
        for inventory in queryset:
            products = Product.objects.filter(inventory=inventory)
            inventory_data[inventory] = products

        product = Product.objects.all()
        context['product'] = product
        context['inventory_data'] = inventory_data
        return context

    def post(self, request, *args, **kwargs):
        # If a POST request is received, redirect to the same view with the POST data as GET parameters
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if start_date and end_date:
            return HttpResponseRedirect(reverse('inventory') + f'?start_date={start_date}&end_date={end_date}')
        else:
            return HttpResponseRedirect(reverse('inventory'))


class ManageInventoryView(View):
    def get(self, request, *args, **kwargs):

        pro_id = self.kwargs['pro_id']
        action = request.GET.get('action')
        pro_obj = Product.objects.get(id=pro_id)
        inventory_obj = pro_obj.inventory

        if action == 'rmv':
            inventory_obj.total -= pro_obj.buy_price
            inventory_obj.save()
            pro_obj.delete()
        else:
            pass
        return redirect('add_new')


# class InventoryView(TemplateView):
#     template_name = 'inventory.html'

#     def post(self, request, *args, **kwargs):
#         product_form = ProductForm(request.POST)
#         supplier_form = SupplierForm(request.POST)
#         category_form = CategoryForm(request.POST)

#         if product_form.is_valid():
#             # Process product form submission
#             product = product_form.save(commit=False)
#             product.save()
#             inventory_id = request.session.get("inventory_id")
#             try:
#                 inventory_obj = Inventory.objects.get(id=inventory_id)
#             except Inventory.DoesNotExist:
#                 inventory_obj = Inventory.objects.create(
#                     user=request.user, total=0)
#                 request.session['inventory_id'] = inventory_obj.id

#             product.inventory = inventory_obj
#             product.save()
#             inventory_obj.total += product.buy_price * product.qty
#             inventory_obj.save()
#             messages.success(
#                 request, f'{product.name} has been added to inventory')
#         elif supplier_form.is_valid():
#             supplier = supplier_form.save()
#             messages.success(
#                 request, f'{supplier.name} has been added as a supplier')
#         elif category_form.is_valid():
#             category = category_form.save()
#             messages.success(
#                 request, f'{category.name} has been added as a category')
#         else:
#             messages.error(
#                 request, 'Failed to add data. Please try again.')

#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         if 'add_inventory' in request.POST:
#             del request.session['inventory_id']

#         return self.render_to_response(self.get_context_data(start_date_str=start_date_str, end_date_str=end_date_str))

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         inventory_id = self.request.session.get("inventory_id")
#         print("Inventory ID:", inventory_id)

#         try:
#             start_date_str = self.request.POST.get('start_date')
#             end_date_str = self.request.POST.get('end_date')

#             if start_date_str and end_date_str:
#                 start_date = datetime.strptime(
#                     start_date_str, '%Y-%m-%d').date()
#                 end_date = datetime.strptime(
#                     end_date_str, '%Y-%m-%d').date()

#                 queryset = Inventory.objects.filter(
#                     timestamps__date__gte=start_date,
#                     timestamps__date__lte=end_date
#                 )
#             else:
#                 queryset = Inventory.objects.all()

#             inventory_data = {}
#             for inventory in queryset:
#                 products = Product.objects.filter(inventory=inventory)
#                 inventory_data[inventory] = products

#             inventory_total = sum(
#                 inventory.total for inventory in queryset
#             )

#         except Inventory.DoesNotExist:
#             inventory_total = 0
#             inventory_data = {}
#             queryset = Inventory.objects.none()

#         categories = Category.objects.all()
#         suppliers = Supplier.objects.all()
#         product = Product.objects.all()
#         inventories = Inventory.objects.all()

#         context['product_form'] = ProductForm()
#         context['supplier_form'] = SupplierForm()
#         context['category_form'] = CategoryForm()
#         context['inventory_total'] = inventory_total
#         context['categories'] = categories
#         context['suppliers'] = suppliers
#         context['inventories'] = inventories
#         context['product'] = product
#         context['inventory_data'] = inventory_data
#         return context
