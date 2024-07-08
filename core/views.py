from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from product.models import Product,Order
from django.db.models import Sum
from datetime import datetime
from django.contrib import messages
from .forms import StaffCreationForm,ProfileUpdateForm
from .models import Staff,ShopOwner
from .filters import StaffFilter
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from product.models import Product, Order, OrderProduct
from transaction.models import Transaction, Payment, Expense
from django.http import HttpResponse
from django.db.models import Q

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


def user_login(request):
    if request.method == 'POST':
        login_field = request.POST['login']
        password = request.POST['password']

        user = authenticate(request, username=login_field, password=password)
        if user is None:
            try:
                user = User.objects.get(
                    Q(username=login_field) | Q(email=login_field))
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)

            is_shop_owner = ShopOwner.objects.filter(user=user).exists()
            is_employee = Staff.objects.filter(user=user).exists()
            is_admin = user.is_staff  

            if is_admin:
               
                return redirect('admin_dashboard')
            elif is_shop_owner:
                
                return redirect('admin_home')
            elif is_employee:
                
                return redirect('cart')
            else:
                return HttpResponse("User role not defined.", status=403)

        return HttpResponse("Invalid credentials.", status=401)

    return render(request, 'login.html')

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
        orderProducts = OrderProduct.objects.all()
        transactions = Transaction.objects.filter(
            transaction_type__in=['payment', 'expense'])

        # Data processing for charts
        product_count = products.count()
        order_count = orders.count()
        orderProduct_count = orderProducts.count()
        transaction_count = transactions.count()

        total_buy_price = sum(product.buy_price for product in products)
        total_sell_price = sum(product.sell_price for product in products)
        total_order_price = sum(order.total for order in orders)

        # Calculate total cost of products in orders
        total_order_product_cost = sum(orderProduct.product.buy_price for orderProduct in orderProducts)
        total_sell_revenue = total_order_price-total_order_product_cost
        # Calculate total expenses from transactions
        total_expenses = sum(transaction.amount for transaction in transactions if transaction.transaction_type == 'expense')

        # Calculate revenue
        revenue = total_sell_revenue -total_expenses

        context = {
            'order_count': order_count,
            'product_count': product_count,
            'transaction_count': transaction_count,
            'orderProduct_count': orderProduct_count,
            'total_buy_price': total_buy_price,
            'total_sell_price': total_sell_price,
            'total_order_price': total_order_price,
            'total_transactions': transaction_count,
            'transactions': transactions,
            'revenue': revenue  # Add the calculated revenue to the context
        }

        return render(request, self.template_name, context)


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('user_login')
