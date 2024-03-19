from django.shortcuts import render
from django.http import HttpResponse
from .form import ProductForm, CategoryForm
from .models import Product, Category
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect


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
