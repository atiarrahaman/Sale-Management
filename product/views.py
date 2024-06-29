from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from inventory.models import  Category, Supplier
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import Cart, CartProduct, Order, OrderProduct, ReturnProduct
from django.views.generic import View, ListView, TemplateView
from django.contrib import messages
from .form import CartProductForm, OrderForm
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .form import ProductForm, ReturnProductForm
from datetime import datetime
from django.http import HttpResponseNotAllowed
from django.db.models import Sum,Q
from datetime import timedelta
from django.utils import timezone

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

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product')
        product_obj = get_object_or_404(Product, id=product_id)
        cart_id = request.session.get("cart_id")

        try:
            cart_obj = Cart.objects.get(id=cart_id)
        except ObjectDoesNotExist:
            cart_obj = Cart.objects.create(user=request.user, total=0)
            request.session['cart_id'] = cart_obj.id

        form = CartProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if int(quantity) > int(product_obj.qty):
                messages.error(
                    request, f'Cannot add {quantity} {product_obj.unit} of {product_obj.name} to the cart. Only {product_obj.qty} available.')
            else:
                cartproduct = form.save(commit=False)
                cartproduct.cart = cart_obj
                cartproduct.quantity = quantity
                cartproduct.price = product_obj.sell_price
                cartproduct.subtotal = product_obj.sell_price * \
                    Decimal(quantity)
                cartproduct.save()
                cart_obj.total += cartproduct.subtotal
                cart_obj.save()
                messages.success(
                    request, f'{product_obj.name} has been added to the cart')
        else:
            messages.error(
                request, 'Failed to add product to the cart. Please try again.')

        return redirect('cart')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")
        try:
            cart_obj = Cart.objects.get(id=cart_id)
            cart_products = cart_obj.cartproduct_set.all()
            cart_total = cart_obj.total
        except ObjectDoesNotExist:
            cart_products = []
            cart_total = 0

        context['form'] = CartProductForm()
        context['cart_products'] = cart_products
        context['cart_total'] = cart_total
        return context


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
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()

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
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        product_name = request.POST.get('product_name')

        filters = Q()
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filters &= Q(created_at__date__gte=start_date,
                         created_at__date__lte=end_date)

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
            order_product.quantity += return_product.return_quantity
            order_product.save()

            messages.success(request, 'Product returned successfully.')
            return redirect('all_order')  # Adjust to your success URL
        else:
            messages.error(
                request, 'Failed to return product. Please check the form.')
            print("Form errors:", form.errors)
            # Return the form with errors to the template
            context = {'form': form}
            return render(request, 'all_order.html', context)
    else:
        form = ReturnProductForm()

    context = {'form': form}
    return render(request, 'all_order.html', context)
