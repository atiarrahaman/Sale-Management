from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Inventory, Category, Supplier, ReturnToSupplier,Brand
from django.views.generic import CreateView, TemplateView
from . forms import CategoryForm, SupplierForm, BrandForm, QuantityForm
from product.models import Product, DamageProduct
from django.db import transaction
from product .form import ProductForm, DamageProductForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import datetime
from django.views import View
from .filters import ProductFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum, F, FloatField
from django.db.models.functions import TruncMonth
from datetime import date
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q
# Create your views here.


class SupplierView(TemplateView):
    template_name = 'add_supplier.html'

    def post(self, request, *args, **kwargs):
        supplier_id = request.POST.get('supplier_id')
        if supplier_id:
            # Editing existing supplier
            supplier = get_object_or_404(Supplier, pk=supplier_id)
            supplier_form = SupplierForm(request.POST, instance=supplier)
        else:
            # Creating new supplier
            supplier_form = SupplierForm(request.POST)

        if supplier_form.is_valid():
            supplier = supplier_form.save()
            messages.success(
                request, f'{supplier.name} has been added/updated as a supplier')
        else:
            messages.error(
                request, 'Failed to add/update supplier. Please try again.')

        return redirect('add_supplier')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier_form'] = SupplierForm()
        context['suppliers'] = Supplier.objects.all()
        return context
    
class SupplierDeleteView(View):
    def get(self, request, pk, *args, **kwargs):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()
        messages.success(request, f'{supplier.name} has been deleted.')
        return redirect('add_supplier')


class BrandCategoryView(TemplateView):
    template_name = 'category_brand.html'

    def post(self, request, *args, **kwargs):
        category_form = CategoryForm(request.POST, prefix='category')
        brand_form = BrandForm(request.POST, prefix='brand')

        if 'category_submit' in request.POST:
            if category_form.is_valid():
                category = category_form.save()
                messages.success(
                    request, f'{category.name} has been added as a category')
                return redirect('brand_category')
            else:
                messages.error(
                    request, 'Failed to add category. Please correct the errors.')

        if 'brand_submit' in request.POST:
            if brand_form.is_valid():
                brand = brand_form.save()
                messages.success(
                    request, f'{brand.name} has been added as a brand')
                return redirect('brand_category')
            else:
                messages.error(
                    request, 'Failed to add brand. Please correct the errors.')

        context = self.get_context_data(
            category_form=category_form, brand_form=brand_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('category_form', CategoryForm(prefix='category'))
        context.setdefault('brand_form', BrandForm(prefix='brand'))
        context['categories'] = Category.objects.all().order_by('-id')
        context['brands'] = Brand.objects.all().order_by('-id')
        return context


class DeleteCategoryOrBrandView(View):
    def post(self, request, pk, model_type, *args, **kwargs):
        if model_type == 'category':
            instance = get_object_or_404(Category, pk=pk)
            instance_name = instance.name
            instance.delete()
            messages.success(request, f'Category "{instance_name}" has been deleted.')
        elif model_type == 'brand':
            instance = get_object_or_404(Brand, pk=pk)
            instance_name = instance.name
            instance.delete()
            messages.success(request, f'Brand "{instance_name}" has been deleted.')
        else:
            messages.error(request, 'Invalid operation.')
        
        return redirect('brand_category')


def download_barcode_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.barcode_image:
        response = HttpResponse(product.barcode_image, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename=barcode_{product_id}.png'
        return response
    else:
        messages.error(request, 'Barcode image not found')
        return redirect('add_product')
    

class NewProductView(TemplateView):
    template_name = 'new_product.html'

    def generate_barcode_image(self, barcode_value):
        code128 = barcode.get_barcode_class('code128')
        barcode_image = code128(barcode_value, writer=ImageWriter())
        buffer = BytesIO()
        barcode_image.write(buffer)
        return ContentFile(buffer.getvalue())

    def post(self, request, *args, **kwargs):
        if 'search_product' in request.POST and 'add_quantity' not in request.POST:
            # Search for existing product
            search_value = request.POST.get('search_product')
            product = None
            if search_value:
                try:
                    product = Product.objects.get(
                        Q(id=search_value) | Q(barcode=search_value))
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

        elif 'add_quantity' in request.POST:
            # Adding quantity to existing product
            quantity_form = QuantityForm(request.POST)
            if quantity_form.is_valid():
                product = quantity_form.cleaned_data['product']
                quantity = quantity_form.cleaned_data['quantity']

                product.qty += quantity
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

                inventory_obj.total += product.buy_price * quantity
                inventory_obj.save()

                messages.success(request, f'Quantity added to {product.name}')
            else:
                for field, errors in quantity_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error in {field}: {error}')
                messages.error(request, 'Failed to add quantity. Please try again.')

            return redirect('add_product')

        else:
            # Adding new product
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

                with transaction.atomic():
                    product.save()
                    product.serial_key = product.generate_serial_key()
                    product.save()

                barcode_value = product.serial_key
                barcode_image_data = self.generate_barcode_image(barcode_value)

                product.barcode = barcode_value
                product.barcode_image.save(
                    f'{barcode_value}.png', barcode_image_data)

                supplier_id = request.POST.get('supplier')
                if supplier_id:
                    try:
                        supplier = Supplier.objects.get(id=supplier_id)
                        supplier.total_amount += product.subtotal
                        supplier.unpaid_amount += product.subtotal
                        supplier.save()
                    except Supplier.DoesNotExist:
                        messages.error(request, 'Supplier not found')
                        return redirect('add_product')

                with transaction.atomic():
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

                context = self.get_context_data(product_id=product.id)
                return self.render_to_response(context)
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
        context['quantity_form'] = QuantityForm()
        context['inventory_products'] = inventory_products
        context['inventory_total'] = inventory_total
        context['suppliers'] = Supplier.objects.all()
        context['products'] = Product.objects.all()
        context['product_id'] = kwargs.get('product_id', None)
        return context


class AllProductView(View):
    template_name = 'all_product.html'

    def post(self, request, *args, **kwargs):
        damage_form = DamageProductForm(request.POST)
        if damage_form.is_valid():
            product = damage_form.cleaned_data['damage_product']
            quantity = damage_form.cleaned_data['damage_quantity']

            # Reduce the quantity in the Product table
            product.qty -= quantity
            product.save()

            # Check if the product already exists in DamageProduct
            try:
                damage_product = DamageProduct.objects.get(
                    damage_product=product)
                damage_product.damage_quantity += quantity
                damage_product.is_returned = False
                damage_product.save()
                messages.success(
                    request, f'{product.name} already exists in damaged products. Quantity increased by {quantity}.')
            except DamageProduct.DoesNotExist:
                damage_form.save()
                messages.success(
                    request, f'{product.name} has been marked as damaged. Quantity reduced by {quantity}.')
        else:
            messages.error(
                request, 'Failed to submit damage form. Please correct the errors.')

        return redirect('all_product')

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
            'interest': interest,
            'damage_form': DamageProductForm()
        }
        return render(request, self.template_name, context)


class InventoryView(TemplateView):
    template_name = 'inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        product_name = self.request.GET.get('product_name')
        category_id = self.request.GET.get('category')
        supplier_id = self.request.GET.get('supplier')

        filters = {}
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filters['date__gte'] = start_date
            filters['date__lte'] = end_date

        queryset = Inventory.objects.filter(**filters)
        inventory_data = {}
        grand_total = 0

        for inventory in queryset:
            products = Product.objects.filter(inventory=inventory)

            if product_name:
                products = products.filter(name__icontains=product_name)
            if category_id:
                products = products.filter(category_id=category_id)
            if supplier_id:
                products = products.filter(supplier_id=supplier_id)

            total = inventory.total
            if total is None:
                total = 0
            grand_total += total

            product_data = []
            for product in products:
                subtotal = product.qty * product.buy_price
                product_data.append({
                    'product': product,
                    'subtotal': subtotal,
                })

            inventory_data[inventory] = product_data

        categories = Category.objects.all()
        suppliers = Supplier.objects.all()

        context['categories'] = categories
        context['suppliers'] = suppliers
        context['inventory_data'] = inventory_data
        context['grand_total'] = grand_total
        context['category_id'] = category_id
        context['supplier_id'] = supplier_id
        return context

    def post(self, request, *args, **kwargs):
        # If a POST request is received, redirect to the same view with the POST data as GET parameters
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        params = f'?start_date={start_date}&end_date={end_date}&product_name={product_name}&category={category_id}&supplier={supplier_id}'
        return HttpResponseRedirect(reverse('inventory') + params)
    
    
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



class ReturnToSupplierProductListView(TemplateView):
    template_name = 'return_to_supplier.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return_products = ReturnToSupplier.objects.all().order_by("-id")

        # Calculate total return quantity
        total_return_quantity = return_products.aggregate(
            total_quantity=Sum('return_quantity')
        )['total_quantity'] or 0

        # Calculate total return price
        total_return_price = return_products.aggregate(
            total_price=Sum(
                F('return_quantity') * F('product__buy_price'),
                output_field=FloatField()
            )
        )['total_price'] or 0

        context['return_products'] = return_products
        context['total_return_quantity'] = total_return_quantity
        context['total_return_price'] = total_return_price

        return context


