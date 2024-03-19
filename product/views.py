from django.shortcuts import render
from django.http import HttpResponse
from .form import ProductForm, CategoryForm
from .models import Product, Category
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import Cart,CartProduct
from django.views.generic import View,ListView, TemplateView
from django.contrib import messages
from .form import CartProductForm
class AddProductView(CreateView):
    template_name = 'add_product.html'
    success_url = ''

    def get(self, request):
        product_form = ProductForm()
        category_form = CategoryForm()
        return render(request, self.template_name, {'product_form': product_form, 'category_form': category_form})

    def post(self, request):
        product_form = ProductForm(request.POST)
        category_form = CategoryForm(request.POST)

        if 'product_submit' in request.POST:
            if product_form.is_valid():
                product_form.save()
                return redirect('product')
        elif 'category_submit' in request.POST:
            if category_form.is_valid():
                category_form.save()
                return redirect('product')

        return render(request, self.template_name, {'product_form': product_form, 'category_form': category_form})


class CartView(TemplateView):
    template_name = 'cart.html'
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product')
        product_obj = Product.objects.get(id=product_id)
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = Cart.objects.create(user=request.user, total=0)
            request.session['cart_id'] = cart_obj.id

        form = CartProductForm(request.POST)
        if form.is_valid():
            cartproduct = form.save(commit=False)
            cartproduct.cart = cart_obj
            cartproduct.quantity = form.cleaned_data['quantity']
            cartproduct.price=product_obj.price
            cartproduct.subtotal = product_obj.price * cartproduct.quantity
            cartproduct.save()
            cart_obj.total += cartproduct.subtotal
            cart_obj.save()
            messages.success(
                request, f'{product_obj.name} has been added to cart')
        else:
            messages.error(
                request, 'Failed to add product to cart. Please try again.')

        return redirect('cart')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Query cart products and total price
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cart_products = CartProduct.objects.filter(cart=cart_obj)
            cart_total = cart_obj.total
        else:
            cart_products = []
            cart_total = 0

        context['form'] = CartProductForm()  # Initialize an empty form
        context['cart_products'] = cart_products
        context['cart_total'] = cart_total
        return context


class ManageCartView(View):
    def get(self, request, *args, **kwargs):

        cp_id = self.kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.price
            cp_obj.save()
            cart_obj.total += cp_obj.price
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.price
            cp_obj.save()
            cart_obj.total -= cp_obj.price
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('cart')
