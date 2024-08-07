from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from inventory.models import  Category, Supplier,ReturnToSupplier
from inventory.forms import ReturnToSupplierForm
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import Cart, CartProduct, Order, OrderProduct, ReturnProduct,DamageProduct
from django.views.generic import View, ListView, TemplateView
from django.contrib import messages
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .form import ProductForm, ReturnProductForm,DamageProductForm,CartProductForm, OrderForm
from datetime import datetime
from django.http import HttpResponseNotAllowed
from django.db.models import Sum,Q, F, FloatField
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from transaction.models import Transaction, Balance

class AddProductView(CreateView):
    template_name = 'add_product.html'
    success_url = ''

    def get(self, request):
        product_form = ProductForm()
        return render(request, self.template_name, {'product_form': product_form})

    def post(self, request):
        product_form = ProductForm(request.POST)

        if product_form.is_valid():
            product_form.save()
            return redirect('product')

        return render(request, self.template_name, {'product_form': product_form})


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")

        try:
            cart_obj = Cart.objects.get(id=cart_id)
            cart_products = cart_obj.cartproduct_set.all()
            cart_total = cart_obj.total
            cart_discount = int(cart_obj.discount)
            cart_vat = int(cart_obj.vat)
            discount_amount, vat_amount = cart_obj.update_cart_total()
        except ObjectDoesNotExist:
            cart_products = []
            cart_total = Decimal('0.00')
            cart_discount = 0
            cart_vat = 15
            discount_amount = Decimal('0.00')
            vat_amount = Decimal('0.00')

        context['form'] = CartProductForm()
        context['order_form'] = OrderForm()
        context['products'] = Product.objects.all()
        context['cart_products'] = cart_products
        context['cart_total'] = cart_total
        context['cart_discount'] = cart_discount
        context['cart_vat'] = cart_vat
        context['discount_amount'] = discount_amount
        context['vat_amount'] = vat_amount
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'add_to_cart':
            product_id = request.POST.get('product')
            product_obj = get_object_or_404(Product, id=product_id)
            cart_id = request.session.get("cart_id")

            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                cart_obj = Cart.objects.create(
                    user=request.user, total=Decimal('0.00'))
                request.session['cart_id'] = cart_obj.id

            quantity = 1  # Default quantity
            if 'quantity' in request.POST:
                quantity = int(request.POST.get('quantity', 1))

            if quantity > product_obj.qty:
                messages.error(
                    request, f'Cannot add {quantity} {product_obj.unit} of {product_obj.name} to the cart. Only {product_obj.qty} available.')
            else:
                cartproduct, created = CartProduct.objects.get_or_create(
                    cart=cart_obj, product=product_obj,
                    defaults={'quantity': quantity, 'price': product_obj.sell_price,
                              'subtotal': product_obj.sell_price * Decimal(quantity)}
                )
                if not created:
                    cartproduct.quantity += quantity
                    cartproduct.subtotal += product_obj.sell_price * \
                        Decimal(quantity)
                    cartproduct.save()

                # Update cart total
                cart_obj.update_cart_total()
                messages.success(
                    request, f'{product_obj.name} has been added to the cart')

            return redirect('cart')

        elif action == 'place_order':
            cart_id = request.session.get("cart_id")

            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                cart_obj = None

            order_form = OrderForm(request.POST)
            if order_form.is_valid() and cart_obj:
                order = order_form.save(commit=False)
                order.total = cart_obj.total
                order.discount = cart_obj.discount
                order.vat = cart_obj.vat
                order.save()

                for cart_product in cart_obj.cartproduct_set.all():
                    # Update product quantity
                    product = cart_product.product
                    if product.qty is not None and cart_product.quantity <= product.qty:
                        product.qty -= cart_product.quantity
                        product.save()

                        # Create OrderProduct
                        OrderProduct.objects.create(
                            order=order,
                            product=cart_product.product,
                            price=cart_product.price,
                            quantity=cart_product.quantity,
                            subtotal=cart_product.subtotal
                        )
                    else:
                        messages.error(
                            request, f'Not enough stock for {product.name}.')
                        return redirect('cart')

                # Create Transaction record for the sale
                shop_owner = request.user.shopowner
                balance, created = Balance.objects.get_or_create(
                    user=shop_owner)

                # Create Transaction record for the sale
                balance.amount += cart_obj.total
                balance.save()

                Transaction.objects.create(
                    transaction_type='sale',
                    amount=cart_obj.total,
                    balance_after_transaction=balance.amount,
                    description=f"Sale for order {order.id}"
                )

                # Fetch discount and VAT amounts for the order
                discount_amount, vat_amount = cart_obj.update_cart_total()

                cart_obj.cartproduct_set.all().delete()
                del request.session['cart_id']
                messages.success(request, 'Order placed successfully!')

                print_template = render_to_string('print_order.html', {
                    'order': order,
                    'order_products': order.orderproduct_set.all(),
                    'order_total': order.total,
                    'order_discount': order.discount,
                    'order_vat': order.vat,
                    'discount_amount': discount_amount,
                    'vat_amount': vat_amount,
                })

                return HttpResponse(print_template)

            context = self.get_context_data()
            context['order_form'] = order_form
            return self.render_to_response(context)

        return redirect('cart')

class UpdateCartSettingsView(View):
    def post(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
                cart_discount = request.POST.get('cart_discount')
                cart_vat = request.POST.get('cart_vat')

                if cart_discount:
                    try:
                        cart_obj.discount = float(cart_discount)
                    except ValueError:
                        messages.error(request, 'Invalid discount value.')
                        return redirect('cart')

                if cart_vat:
                    try:
                        cart_obj.vat = float(cart_vat)
                    except ValueError:
                        messages.error(request, 'Invalid VAT value.')
                        return redirect('cart')

                cart_obj.update_cart_total()
                messages.success(
                    request, 'Cart settings updated successfully!')
            except Cart.DoesNotExist:
                messages.error(request, 'Cart not found.')

        return redirect('cart')
# class CartView(TemplateView):
#     template_name = 'cart.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         cart_id = self.request.session.get("cart_id")

#         try:
#             cart_obj = Cart.objects.get(id=cart_id)
#             cart_products = cart_obj.cartproduct_set.all()
#             cart_total = cart_obj.total
#         except ObjectDoesNotExist:
#             cart_products = []
#             cart_total = 0

#         context['form'] = CartProductForm()
#         context['order_form'] = OrderForm()
#         context['products'] = Product.objects.all()
#         context['cart_products'] = cart_products
#         context['cart_total'] = cart_total
#         return context

#     def post(self, request, *args, **kwargs):
#         action = request.POST.get('action')

#         if action == 'add_to_cart':
#             product_id = request.POST.get('product')
#             product_obj = get_object_or_404(Product, id=product_id)
#             cart_id = request.session.get("cart_id")

#             try:
#                 cart_obj = Cart.objects.get(id=cart_id)
#             except ObjectDoesNotExist:
#                 cart_obj = Cart.objects.create(user=request.user, total=0)
#                 request.session['cart_id'] = cart_obj.id

#             quantity = 1  # Default quantity
#             if 'quantity' in request.POST:
#                 quantity = int(request.POST.get('quantity', 1))

#             if quantity > product_obj.qty:
#                 messages.error(
#                     request, f'Cannot add {quantity} {product_obj.unit} of {product_obj.name} to the cart. Only {product_obj.qty} available.')
#             else:
#                 cartproduct, created = CartProduct.objects.get_or_create(
#                     cart=cart_obj, product=product_obj,
#                     defaults={'quantity': quantity, 'price': product_obj.sell_price,
#                               'subtotal': product_obj.sell_price * Decimal(quantity)}
#                 )
#                 if not created:
#                     cartproduct.quantity += quantity
#                     cartproduct.subtotal += product_obj.sell_price * \
#                         Decimal(quantity)
#                     cartproduct.save()
#                 cart_obj.total += product_obj.sell_price * Decimal(quantity)
#                 cart_obj.save()
#                 messages.success(
#                     request, f'{product_obj.name} has been added to the cart')

#             return redirect('cart')

#         elif action == 'place_order':
#             cart_id = request.session.get("cart_id")

#             try:
#                 cart_obj = Cart.objects.get(id=cart_id)
#             except ObjectDoesNotExist:
#                 cart_obj = None

#             order_form = OrderForm(request.POST)
#             if order_form.is_valid() and cart_obj:
#                 order = order_form.save(commit=False)
#                 order.total = cart_obj.total
#                 order.save()

#                 for cart_product in cart_obj.cartproduct_set.all():
#                     # Update product quantity
#                     product = cart_product.product
#                     if product.qty is not None and cart_product.quantity <= product.qty:
#                         product.qty -= cart_product.quantity
#                         product.save()

#                         # Create OrderProduct
#                         OrderProduct.objects.create(
#                             order=order,
#                             product=cart_product.product,
#                             price=cart_product.price,
#                             quantity=cart_product.quantity,
#                             subtotal=cart_product.subtotal
#                         )
#                     else:
#                         messages.error(
#                             request, f'Not enough stock for {product.name}.')
#                         # Redirect to order page if stock is insufficient
#                         return redirect('cart')

#                 # Create Transaction record for the sale            
#                 shop_owner = request.user.shopowner
#                 balance, created = Balance.objects.get_or_create(
#                     user=shop_owner)

#                 # Create Transaction record for the sale
#                 balance.amount += cart_obj.total
#                 balance.save()

#                 Transaction.objects.create(
#                     transaction_type='sale',
#                     amount=cart_obj.total,
#                     balance_after_transaction=balance.amount,
#                     description=f"Sale for order {order.id}"
#                 )

#                 cart_obj.cartproduct_set.all().delete()
#                 del request.session['cart_id']
#                 messages.success(request, 'Order placed successfully!')

#                 print_template = render_to_string('print_order.html', {
#                     'order': order,
#                     'order_products': order.orderproduct_set.all(),
#                     'order_total': order.total
#                 })

#                 return HttpResponse(print_template)

#             context = self.get_context_data()
#             context['order_form'] = order_form
#             return self.render_to_response(context)

#         return redirect('cart')


class ManageCartView(View):
    def post(self, request, cp_id):
        cp_obj = get_object_or_404(CartProduct, id=cp_id)
        cart_obj = cp_obj.cart

        # Update price
        if 'price' in request.POST:
            price = float(request.POST['price'])
            cp_obj.price = price
            cp_obj.subtotal = price * cp_obj.quantity
            cp_obj.save()
            cart_obj.update_cart_total()

        # Update quantity
        elif 'quantity' in request.POST:
            quantity = int(request.POST['quantity'])
            cp_obj.quantity = quantity
            cp_obj.subtotal = cp_obj.price * quantity
            cp_obj.save()
            cart_obj.update_cart_total()

        return redirect('cart')

    def get(self, request, cp_id):
        cp_obj = get_object_or_404(CartProduct, id=cp_id)
        cart_obj = cp_obj.cart

        action = request.GET.get('action')

        # Handle increment quantity
        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.price
            cp_obj.save()
            cart_obj.update_cart_total()

        # Handle decrement quantity
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.price
            cp_obj.save()
            cart_obj.update_cart_total()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        # Handle remove product from cart
        elif action == 'rmv':
            cp_obj.delete()
        cart_obj.update_cart_total()

        return redirect('cart')


class OrderView(TemplateView):
    template_name = 'order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_form'] = OrderForm()

        # Retrieve the order and order products
        cart_id = self.request.session.get("cart_id")
        try:
            cart_obj = Cart.objects.get(id=cart_id)
            order_products = cart_obj.cartproduct_set.all()
            cart_total = cart_obj.total
        except ObjectDoesNotExist:
            order_products = []
            cart_total = 0

        context['order_products'] = order_products
        context['order_total'] = cart_total
        return context

    def post(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")

        try:
            cart_obj = Cart.objects.get(id=cart_id)
        except ObjectDoesNotExist:
            cart_obj = None

        order_form = OrderForm(request.POST)
        if order_form.is_valid() and cart_obj:
            order = order_form.save(commit=False)
            order.total = cart_obj.total
            order.save()

            for cart_product in cart_obj.cartproduct_set.all():
                # Update product quantity
                product = cart_product.product
                if product.qty is not None and cart_product.quantity <= product.qty:
                    product.qty -= cart_product.quantity
                    product.save()

                    # Create OrderProduct
                    OrderProduct.objects.create(
                        order=order,
                        product=cart_product.product,
                        price=cart_product.price,
                        quantity=cart_product.quantity,
                        subtotal=cart_product.subtotal
                    )
                else:
                    messages.error(
                        request, f'Not enough stock for {product.name}.')
                    # Redirect to order page if stock is insufficient
                    return redirect('order')

            cart_obj.cartproduct_set.all().delete()
            del request.session['cart_id']
            messages.success(request, 'Order placed successfully!')
            


            print_template = render_to_string('print_order.html', {
                'order': order,
                'order_products': order.orderproduct_set.all(),
                'order_total': order.total
            })

            return HttpResponse(print_template)

        context = self.get_context_data()
        context['order_form'] = order_form
        return self.render_to_response(context)


class AllOrderView(TemplateView):
    template_name = 'all_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Order.objects.all()
        grand_total = queryset.aggregate(total=Sum('total'))['total'] or 0

        now = timezone.now().date()
        order_data = {
            order: {
                'products': OrderProduct.objects.filter(order=order),
                'returnable': (now - order.created_at.date()).days <= 7
            } for order in queryset
        }

        context['order_data'] = order_data
        context['grand_total'] = grand_total
        return context

    def post(self, request, *args, **kwargs):
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        invoice = request.POST.get('invoice')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        product_name = request.POST.get('product_name')

        filters = Q()
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filters &= Q(created_at__date__gte=start_date,
                         created_at__date__lte=end_date)

        if invoice:
            filters &= Q(invoice__icontains=invoice)
        if name:
            filters &= Q(name__icontains=name)

        if phone:
            filters &= Q(phone__icontains=phone)

        if product_name:
            order_ids = OrderProduct.objects.filter(
                product__name__icontains=product_name).values_list('order_id', flat=True)
            filters &= Q(id__in=order_ids)

        queryset = Order.objects.filter(filters)
        grand_total = queryset.aggregate(total=Sum('total'))['total'] or 0

        now = timezone.now().date()
        order_data = {
            order: {
                'products': OrderProduct.objects.filter(order=order),
                'returnable': (now - order.created_at.date()).days <= 7
            } for order in queryset
        }

        context = {
            'order_data': order_data,
            'grand_total': grand_total,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'name': name,
            'phone': phone,
            'product_name': product_name,
        }
        return render(request, self.template_name, context)


def return_product(request):
    if request.method == 'POST':
        form = ReturnProductForm(request.POST)
        if form.is_valid():
            return_product = form.save()

            order_product = return_product.order_product
            product = order_product.product

            # Set the is_returned field to True
            order_product.is_returned = True
            order_product.save()

            if return_product.is_damage:
                # Handle damaged product logic (e.g., save to damage product table)
                messages.success(
                    request, 'Damaged product recorded successfully.')
            else:
                # Increase product quantity by return quantity
                product.qty += return_product.return_quantity
                product.save()

            messages.success(request, 'Product returned successfully.')
            return redirect('all_order')  # Adjust to your success URL
        else:
            messages.error(
                request, 'Failed to return product. Please check the form.')
            context = {'form': form}
            return render(request, 'all_order.html', context)
    else:
        form = ReturnProductForm()

    context = {'form': form}
    return render(request, 'all_order.html', context)

class ReturnProductListView(TemplateView):
    template_name = 'return_product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return_products = ReturnProduct.objects.filter(
            is_damage=False).order_by("-id")

        total_return_quantity = return_products.aggregate(
            total_quantity=Sum('return_quantity'))['total_quantity'] or 0
        total_return_price = return_products.aggregate(
            total_price=Sum(F('return_quantity') *
                            F('order_product__price'), output_field=FloatField())
        )['total_price'] or 0

        context['return_products'] = return_products
        context['total_return_quantity'] = total_return_quantity
        context['total_return_price'] = total_return_price
        return context


class DamageProductListView(TemplateView):
    template_name = 'damage_product_list.html'

    def post(self, request, *args, **kwargs):
        return_form = ReturnToSupplierForm(request.POST)
        if return_form.is_valid():
            return_to_supplier = return_form.save(commit=False)
            product = return_to_supplier.product
            return_quantity = return_to_supplier.return_quantity

            try:
                damage_product = DamageProduct.objects.get(
                    damage_product=product, is_returned=False)
                if damage_product.damage_quantity >= return_quantity:
                    return_to_supplier.is_damage = True
                    return_to_supplier.save()

                    # Update the corresponding DamageProduct
                    damage_product.damage_quantity -= return_quantity
                    if damage_product.damage_quantity == 0:
                        damage_product.is_returned = True
                    damage_product.save()

                    messages.success(
                        request, f'{product.name} has been returned. Quantity: {return_quantity}.')
                    return redirect('damage_products')
                else:
                    messages.error(
                        request, f'Return quantity cannot exceed damaged quantity. {product.name} has only {damage_product.damage_quantity} damaged units.')
            except DamageProduct.DoesNotExist:
                messages.error(
                    request, f'No damage record found for the product {product.name}.')

        else:
            messages.error(
                request, 'Failed to submit damage form. Please correct the errors.')

        context = self.get_context_data()
        context['return_form'] = return_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        damage_products = DamageProduct.objects.filter(
            is_returned=False, damage_quantity__gt=0).order_by("-id")
        context['damage_products'] = damage_products
        context['return_form'] = ReturnToSupplierForm()
        return context
def sales_report(request):
    # Get all orders initially
    orders = Order.objects.all()

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # Parse start and end dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter orders by date range
        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date])

    # Initialize data dictionary to store sales report
    sales_report = {}

    for order in orders:
        order_products = OrderProduct.objects.filter(order=order)
        for op in order_products:
            product_id = op.product.id
            product_name = op.product.name
            quantity_sold = op.quantity
            product_price = op.price
            subtotal = op.subtotal

            if product_id not in sales_report:
                sales_report[product_id] = {
                    'product_name': product_name,
                    'quantity_sold': quantity_sold,
                    'product_price': product_price,
                    'subtotal': subtotal
                }
            else:
                sales_report[product_id]['quantity_sold'] += quantity_sold
                sales_report[product_id]['subtotal'] += subtotal

    # Calculate grand total
    grand_total = sum(report['subtotal'] for report in sales_report.values())

    context = {
        'sales_report': sales_report.values(),
        'grand_total': grand_total,
        'start_date': start_date_str if request.method == 'POST' else '',
        'end_date': end_date_str if request.method == 'POST' else '',
    }

    return render(request, 'sales_report.html', context)
