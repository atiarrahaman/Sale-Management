from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from product.models import Product,Order
from transaction.models import Exprensive
from django.utils.decorators import method_decorator
from django.db.models import Sum
from datetime import datetime
from django.contrib import messages
from .forms import StaffCreationForm,ProfileUpdateForm
from .models import Staff
from .filters import StaffFilter
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView


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

    def get_queryset(self):
        queryset = Exprensive.objects.all()
        self.balance = queryset.aggregate(Sum('amount'))['amount__sum']
        self.total = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        return queryset

    def get(self, request, *args, **kwargs):
        product = Product.objects.all()
        order=Order.objects.all()
        context = {
            'object_list': self.get_queryset(),
            'balance': self.balance,
            'total': self.total,
            'product': product,
            'order': order,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = Exprensive.objects.filter(
                timestamps__date__gte=start_date,
                timestamps__date__lte=end_date
            )
            self.balance = queryset.aggregate(Sum('amount'))['amount__sum']
            self.total = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

            context = {
                'object_list': queryset,
                'balance': self.balance,
                'total': self.total,
            }

            return render(request, self.template_name, context)

        return redirect('admin_dashboard')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('user_login')
