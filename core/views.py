from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from product.models import Product,Order
from transaction.models import Expense
from django.utils.decorators import method_decorator
from django.db.models import Sum
from datetime import datetime
from django.contrib import messages
from .forms import StaffCreationForm,ProfileUpdateForm
from .models import Staff
from .filters import StaffFilter
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from product.models import Product, Order, OrderProduct
from transaction.models import Transaction, Payment, Expense

class StaffCreateView(View):
    form_class = StaffCreationForm
    template_name = 'staff_create.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            staff = Staff.objects.create(
                user=user,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                image=form.cleaned_data['image']
            )
            messages.success(request, 'User and Staff created successfully.')
            
            return redirect('add_staff')
        else:
            messages.error(request, 'Error creating user and staff.')
        return render(request, self.template_name, {'form': form})

class StaffProfile(View):
    template_name='staff_profile.html'
    def get(self, request):
        profile=Staff.objects.get(user=request.user)
        context = {
            'profile': profile,
        }
        return render(request, self.template_name, context)


class ProfileUpdateView(View):
    template_name = 'update_profile.html'

    def get(self, request):
        staff_instance = Staff.objects.get(user=request.user)
        form = ProfileUpdateForm(instance=staff_instance)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        staff_instance = Staff.objects.get(user=request.user)
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=staff_instance)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})

class UserLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            messages.success(self.request, "Welcome Admin ")
            return reverse_lazy('admin_home')
        else:
            messages.success(
                self.request, "Welcome! You are successfully logged in.")
        return reverse_lazy('cart')


class AllStaffView(View):
    template_name = 'all_staff.html'

    def get(self, request):
        all_staff = User.objects.filter(is_superuser=False)
        myfilter = StaffFilter(request.GET, queryset=all_staff)
        staff=myfilter.qs
        context = {
            'myfilter': myfilter,
            'staff': staff
        }
        return render(request, self.template_name, context)
    
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('password_change_done') 


class AdminHomeView(View):
    template_name = 'admin_dashboard.html'

    def get(self, request):
        # Fetch data from models
        products = Product.objects.all()
        orders = Order.objects.all()
        orderProduct = OrderProduct.objects.all()
        transactions = Transaction.objects.all()

        # Data processing for charts
        product_count = products.count()
        total_buy_price = sum(product.buy_price for product in products)
        total_sell_price = sum(product.sell_price for product in products)
        total_order_price = sum(order.total for order in orders)
        # total_order_price = sum(orderProduct.price for order in orders)
        total_transactions = transactions.count()

        context = {
            'product_count': product_count,
            'total_buy_price': total_buy_price,
            'total_sell_price': total_sell_price,
            'total_order_price': total_order_price,
            'total_transactions': total_transactions,
            'transactions': transactions
        }

        return render(request, self.template_name, context)


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('user_login')
