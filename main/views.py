from .forms import ContactForm
from django.core.paginator import Paginator
from .models import Category, Product, Order, OrderItem
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')
    template_name = 'change_password.html'

    def form_valid(self, form):
        messages.success(self.request, 'Ваш пароль был успешно изменён!')
        return super().form_valid(form)


def get_cart(request):
    cart = request.session.get('cart', {})
    return sum(item['quantity'] for item in cart.values())


def index(request):
    new_products = Product.objects.filter(is_new=True)[:8]
    hot_sales = Product.objects.filter(is_hot_sales=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True)[:8]

    return render(request, 'index.html', {
        'new_products': new_products,
        'hot_sales': hot_sales,
        'bestsellers': bestsellers,
    })

def catalog(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    sizes = ['XS', 'S', 'M', 'L', 'XL']

    # Фильтрация по категориям
    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    # Фильтрация по размерам
    selected_sizes = request.GET.getlist('sizes')
    if selected_sizes:
        products = products.filter(size__in=selected_sizes)

    # Фильтрация по доступности
    in_stock = request.GET.get('in_stock', 'all')
    if in_stock == 'true':
        products = products.filter(in_stock=True)
    elif in_stock == 'false':
        products = products.filter(in_stock=False)

    # Фильтрация по цене
    price_max = request.GET.get('price_range')
    if price_max:
        try:
            price_max = float(price_max)
            products = products.filter(price__lte=price_max)
        except ValueError:
            pass

    # Сортировка
    sort = request.GET.get('sort', 'best-sellings')
    if sort == 'price-low-to-high':
        products = products.order_by('price')
    elif sort == 'price-high-to-low':
        products = products.order_by('-price')
    elif sort == 'best-sellings':
        products = products.order_by('-is_bestseller', '-created_at')
    else:
        products = products.order_by('-created_at')  # fallback

    # Пагинация
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj.object_list,
        'categories': categories,
        'sizes': sizes,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'current_sort': sort,
        'selected_categories': selected_categories,
        'selected_sizes': selected_sizes,
    }
    return render(request, 'catalog.html', context)

def about(request):
    return render(request, 'about.html')

def change_password_view(request):
    return render(request, 'change_password.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {
        'form': form
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # или другая страница после регистрации
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for product_id, item in cart.items():
        total_price = item['price'] * item['quantity']
        cart_total += total_price
        cart_items.append({
            'product_id': product_id,
            'product_name': item['product_name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total_price': total_price
        })

    if request.method == 'POST':
        order = Order.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip']
        )

        for item in cart_items:
            product = get_object_or_404(Product, pk=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        request.session['cart'] = {}
        return render(request, 'checkout_success.html', {'order': order})

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Здесь можно отправить email, сохранить в БД и т.д.
            # name = form.cleaned_data['name']
            # email = form.cleaned_data['email']
            # phone = form.cleaned_data['phone']
            # message = form.cleaned_data['message']
            pass
    return render(request, 'contact.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def load_products(request):
    tab = request.GET.get('tab')
    products = []

    if tab == 'new':
        products = Product.objects.filter(is_new=True)[:12]
    elif tab == 'sale':
        products = Product.objects.filter(is_hot_sales=True)[:12]
    elif tab == 'best':
        products = Product.objects.filter(is_bestseller=True)[:12]

    html = render_to_string('product_cards.html', {'products': products})
    return JsonResponse({'html': html})

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'product_name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image_url': product.image.url
        }

    request.session['cart'] = cart
    return redirect('cart')

@login_required(login_url='login')
def cart_view(request):
    cart = request.session.get('cart', {})

    cart_items = []
    cart_total = 0

    for product_id, item in cart.items():
        total_price = item['price'] * item['quantity']
        cart_total += total_price

        cart_items.append({
            'id': product_id,
            'product_name': item['product_name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total_price': total_price,
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })

@login_required(login_url='login')
def cart_remove_item(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart

    return redirect('cart')

@require_POST
def cart_update_quantity(request, product_id):
    cart = request.session.get('cart', {})
    operation = request.POST.get('operation')

    if str(product_id) in cart:
        if operation == 'increase':
            cart[str(product_id)]['quantity'] += 1
        elif operation == 'decrease':
            cart[str(product_id)]['quantity'] -= 1
            if cart[str(product_id)]['quantity'] < 1:
                del cart[str(product_id)]
        request.session['cart'] = cart

    return redirect('cart')


def product_search(request):
    search_text = request.GET.get('search_text', '')

    products = Product.objects.all()
    if search_text:
        products = products.filter(name__icontains=search_text)

    return render(request, 'search_results.html', {
        'products': products,
        'search_text': search_text
    })