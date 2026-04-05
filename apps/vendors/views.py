from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from apps.products.models import Product
from apps.services.models import Service
from .models import Store
from .forms import ProductForm

# --- تسجيل الدخول والخروج ---
def vendor_login(request):
    if request.user.is_authenticated:
        return redirect('vendors:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vendors:dashboard')
        else:
            messages.error(request, 'بيانات الدخول غير صحيحة')
    return render(request, 'vendors/login.html')

@login_required(login_url='vendors:login')
def vendor_dashboard(request):
    store, created = Store.objects.get_or_create(vendor=request.user)
    context = {
        'store': store,
        'total_products': Product.objects.filter(vendor=request.user).count(),
        'total_services': Service.objects.filter(vendor=request.user).count(),
    }
    return render(request, 'vendors/dashboard.html', context)

def vendor_logout(request):
    logout(request)
    return redirect('vendors:login')

# --- إدارة المنتجات ---

@login_required(login_url='vendors:login')
def product_list(request):
    products = Product.objects.filter(vendor=request.user)
    return render(request, 'vendors/product_list.html', {'products': products})

@login_required(login_url='vendors:login')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user  # ربط المنتج بالتاجر تلقائياً
            product.save()
            messages.success(request, 'تمت إضافة المنتج')
            return redirect('vendors:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'vendors/product_form.html', {'form': form})

@login_required(login_url='vendors:login')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج')
            return redirect('vendors:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendors/product_form.html', {'form': form})

@login_required(login_url='vendors:login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'تم حذف المنتج')
        return redirect('vendors:product_list')
    return render(request, 'vendors/product_confirm_delete.html', {'product': product})