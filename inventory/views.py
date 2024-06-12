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
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date
# Create your views here.


class SupplierView(TemplateView):
    template_name = 'add_supplier.html'

    def post(self, request, *args, **kwargs):
        supplier_form = SupplierForm(request.POST)
        if supplier_form.is_valid():
            supplier = supplier_form.save()
            messages.success(request, f'{supplier.name} has been added/updated as a supplier')
        else:
            messages.error(request, 'Failed to add/update supplier. Please try again.')
        return redirect('add_supplier')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier_form'] = SupplierForm()
        context['suppliers'] = Supplier.objects.all()
        return context


class CategoryView(TemplateView):
    template_name = 'add_category.html'

    def post(self, request, *args, **kwargs):
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save()
            messages.success(request, f'{category.name} has been added as a category')
        else:
            messages.error(request, 'Failed to add category. Please try again.')
        return redirect('add_category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_form'] = CategoryForm()
        return context


class NewProductView(TemplateView):
    template_name = 'new_product.html'

    def post(self, request, *args, **kwargs):
        if 'search_product' in request.POST:
            search_value = request.POST.get('search_product')
            product = None
            if search_value:
                try:
                    product = Product.objects.get(id=search_value)
                except (Product.DoesNotExist, ValueError):
                    product = Product.objects.filter(
                        name__icontains=search_value).first()
            if product:
                product_form = ProductForm(instance=product)
                context = self.get_context_data(
                    product_form=product_form, product_id=product.id)
                return self.render_to_response(context)
            else:
                messages.error(request, 'Product not found')
                return redirect('add_product')
        else:
            product_id = request.POST.get('product_id')
            if product_id:
                product = Product.objects.get(id=product_id)
                product_form = ProductForm(
                    request.POST, request.FILES, instance=product)
            else:
                product_form = ProductForm(request.POST, request.FILES)

            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.subtotal = product.qty * product.buy_price
                product.save()

                inventory_id = request.session.get("inventory_id")
                today = date.today()
                try:
                    inventory_obj = Inventory.objects.get(
                        id=inventory_id, date=today)
                except Inventory.DoesNotExist:
                    inventory_obj = Inventory.objects.create(
                        user=request.user, date=today, total=0)
                    request.session['inventory_id'] = inventory_obj.id

                product.inventory = inventory_obj
                product.save()
                inventory_obj.total += product.buy_price * product.qty
                inventory_obj.save()
                messages.success(
                    request, f'{product.name} has been added to inventory')
            else:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error in {field}: {error}')
                messages.error(
                    request, 'Failed to add product. Please try again.')

        return redirect('add_product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_id = self.request.session.get("inventory_id")
        today = date.today()

        try:
            inventory_obj = Inventory.objects.get(id=inventory_id, date=today)
            inventory_products = inventory_obj.inventory.all()
            inventory_total = inventory_obj.total
        except Inventory.DoesNotExist:
            inventory_products = []
            inventory_total = 0

        context['product_form'] = kwargs.get('product_form', ProductForm())
        context['inventory_products'] = inventory_products
        context['inventory_total'] = inventory_total
        context['suppliers'] = Supplier.objects.all()
        context['products'] = Product.objects.all()
        context['product_id'] = kwargs.get('product_id', None)
        return context
# class NewProductView(TemplateView):
#     template_name = 'add_new.html'

#     def post(self, request, *args, **kwargs):
#         if 'supplier_id' in request.POST:
#             supplier = Supplier.objects.get(id=request.POST['supplier_id'])
#             supplier_form = SupplierForm(request.POST, instance=supplier)
#         else:
#             supplier_form = SupplierForm(request.POST)

#         product_form = ProductForm(request.POST)
#         category_form = CategoryForm(request.POST)

#         if product_form.is_valid():
#             # Process product form submission
#             product = product_form.save(commit=False)
#             product.subtotal = product.qty * product.buy_price
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
#                 request, f'{supplier.name} has been added/updated as a supplier')
#         elif category_form.is_valid():
#             category = category_form.save()
#             messages.success(
#                 request, f'{category.name} has been added as a category')
#         else:
#             messages.error(request, 'Failed to add data. Please try again.')
#         if 'add_inventory' in request.POST:
#             del request.session['inventory_id']
#         return redirect('add_new')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         inventory_id = self.request.session.get("inventory_id")

#         try:
#             inventory_obj = Inventory.objects.get(id=inventory_id)
#             inventory_products = inventory_obj.inventory.all()
#             inventory_total = inventory_obj.total
#         except Inventory.DoesNotExist:
#             inventory_products = []
#             inventory_total = 0

#         context['product_form'] = ProductForm()
#         context['supplier_form'] = SupplierForm()
#         context['category_form'] = CategoryForm()
#         context['inventory_products'] = inventory_products
#         context['inventory_total'] = inventory_total
#         context['suppliers'] = Supplier.objects.all()

#         return context



class AllProductView(View):
    template_name = 'all_product.html'

    def get(self, request, *args, **kwargs):
        all_product = Product.objects.all()

        myfilter = ProductFilter(request.GET, queryset=all_product)
        products = myfilter.qs

        total_buy_price = products.aggregate(total_buy_price=Sum('buy_price'))[
            'total_buy_price'] or 0
        total_sell_price = products.aggregate(total_sell_price=Sum('sell_price'))[
            'total_sell_price'] or 0
        interest = total_sell_price - total_buy_price

        context = {
            'myfilter': myfilter,
            'product': products,
            'total_buy_price': total_buy_price,
            'total_sell_price': total_sell_price,
            'interest': interest
        }
        return render(request, self.template_name, context)

# class InventoryView(TemplateView):
#     template_name = 'inventory.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         start_date_str = self.request.GET.get('start_date')
#         end_date_str = self.request.GET.get('end_date')

#         if start_date_str and end_date_str:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#             queryset = Inventory.objects.filter(
#                 timestamps__date__gte=start_date, timestamps__date__lte=end_date)
#         else:
#             queryset = Inventory.objects.all()

#         inventory_data = {}
#         grand_total = 0

#         for inventory in queryset:
#             products = Product.objects.filter(inventory=inventory)
#             total = products.aggregate(total=Sum('buy_price'))['total']
#             if total is None:
#                 total = 0
#             grand_total += total
#             month_year = inventory.timestamps.strftime("%B %Y")
#             if month_year not in inventory_data:
#                 inventory_data[month_year] = {
#                     'total': total, 'products': products}
#             else:
#                 inventory_data[month_year]['total'] += total
#                 inventory_data[month_year]['products'] |= products

#         context['inventory_data'] = inventory_data
#         context['grand_total'] = grand_total
#         return context
#     def post(self, request, *args, **kwargs):
#         # If a POST request is received, redirect to the same view with the POST data as GET parameters
#         start_date = request.POST.get('start_date')
#         end_date = request.POST.get('end_date')
#         if start_date and end_date:
#             return HttpResponseRedirect(reverse('inventory') + f'?start_date={start_date}&end_date={end_date}')
#         else:
#             return HttpResponseRedirect(reverse('inventory'))


class InventoryView(TemplateView):
    template_name = 'inventory.html'

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
        grand_total = 0

        for inventory in queryset:
            products = Product.objects.filter(inventory=inventory)
            total = inventory.total
            if total is None:
                total = 0
            grand_total += total
            inventory_data[inventory] = products

        product = Product.objects.all()
        context['product'] = product
        context['inventory_data'] = inventory_data
        context['grand_total'] = grand_total
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
            inventory_obj.total -= pro_obj.subtotal
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
