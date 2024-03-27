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


class UserLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            messages.success(self.request, "Welcome Admin ")
            return reverse_lazy('admin_dashboard')
        else:
            messages.success(
                self.request, "Welcome! You are successfully logged in.")
        return reverse_lazy('staff_dashboard')


class StaffHomeView(View):
    template_name = 'staff_dashboard.html'

    def get(self, request):
        data = Product.objects.all()
        return render(request, self.template_name, {'data': data})


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
    return redirect('login')
