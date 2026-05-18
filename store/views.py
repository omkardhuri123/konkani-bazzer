from typing import cast
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from django.core.paginator import Paginator
from .models import Product, Category, Order, OrderItem, Wishlist
from .forms import UserRegistrationForm, CheckoutForm, LoginForm
# At the top of views.py, add require_POST to your existing imports
from django.views.decorators.http import require_POST
# ====================== Public Pages ======================
class HomeView(TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            featured=True, is_active=True
        )[:8]
        context['categories'] = Category.objects.all()
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'shop.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.select_related('category').filter(is_active=True)
        search_query = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        sort = self.request.GET.get('sort')
        # ✅ AFTER — line break BEFORE the binary operator (PEP 8 preferred style)
        queryset = queryset.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
        )
        if category_id:
            try:
                queryset = queryset.filter(category__id=int(category_id))
            except ValueError:
                pass
            # ✅ AFTER — only catch the specific errors we expect from bad user input.
        # ValueError: raised when Decimal() receives a non-numeric string like "abc"
        # ArithmeticError: parent class covering decimal overflow/invalid operations
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except (ValueError, ArithmeticError):
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except (ValueError, ArithmeticError):
                pass
        # Sorting
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-featured', 'name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.all()
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'sort': self.request.GET.get('sort', ''),
        }
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    # This annotation tells Pylance what type self.object will be at runtime.
    # Django sets it dynamically, so we declare it explicitly for the type checker.
    object: Product

    def get_object(self, queryset=None):
        """Use get_object_or_404 for better error handling"""
        queryset = self.get_queryset()
        return get_object_or_404(queryset, slug=self.kwargs.get('slug'))

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = cast(Product, self.object)
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]
        return context

class CategoryListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    paginate_by = 12                    # Added Pagination
    # This annotation tells Pylance what type self.object will be at runtime.
    # Django sets it dynamically, so we declare it explicitly for the type checker.
    object: Product

    def get_object(self, queryset=None):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = cast(Category, self.object)
        products = Product.objects.filter(
            category=category,
            is_active=True
        )
        # Add pagination to products
        page = self.request.GET.get('page')
        paginator = Paginator(products, self.paginate_by)
        products_page = paginator.get_page(page)
        context['products'] = products_page
        context['paginator'] = paginator
        context['page_obj'] = products_page
        return context
# ====================== Cart, Wishlist, Orders, etc. ======================
def _build_cart_items(session):
    cart = session.get('cart', {}) or {}
    items = []
    total = Decimal('0.00')
    cleaned_cart = {}
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), is_active=True)
        except (Product.DoesNotExist, ValueError):
            continue
        if quantity <= 0:
            continue
        subtotal = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        total += subtotal
        cleaned_cart[str(product.pk)] = quantity
    if cleaned_cart != cart:
        session['cart'] = cleaned_cart
    return items, total

@login_required
def cart_view(request):
    cart_items, total = _build_cart_items(request.session)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
    })

# ✅ AFTER
@login_required
@require_POST
def clear_cart(request):
    request.session['cart'] = {}
    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            qty = 1
    else:
        qty = -1 if request.GET.get('action') == 'decrease' else 1

    current = cart.get(product_key, 0)

    if qty < 0:
        new_qty = max(current + qty, 0)
        if new_qty == 0:
            cart.pop(product_key, None)
        else:
            cart[product_key] = new_qty
    else:
        cart[product_key] = current + qty

    request.session['cart'] = cart
    if qty > 0:
        messages.success(request, '✅ Product added to cart!')
    else:
        messages.info(request, 'Cart updated.')
    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    messages.info(request, 'Product removed from cart.')
    return redirect('cart')

@login_required
def wishlist_view(request):
    products = Product.objects.filter(wishlist__user=request.user, is_active=True).distinct()
    return render(request, 'wishlist.html', {'products': products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, '❤️ Added to wishlist!')
    else:
        messages.info(request, 'Already in wishlist')

    return redirect('wishlist')

# ✅ AFTER — call get_object_or_404 without assigning the result.
# We only call it to verify the product exists (raises 404 if not).
# We don't need the Product object itself for the delete operation.
@login_required
def remove_from_wishlist(request, product_id):
    get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.info(request, 'Product removed from wishlist.')
    return redirect('wishlist')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
# ✅ AFTER — only responds to POST requests
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def checkout(request):
    cart_items, total = _build_cart_items(request.session)
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = total
            order.save()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
            request.session['cart'] = {}
            messages.success(request, 'Order placed successfully!')
            return redirect('order_success', pk=order.id)
    else:
        initial = {
            'first_name': getattr(request.user, 'name', ''),
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial)
    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    })

class OrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_confirmation.html'
    context_object_name = 'order'
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
@login_required
def my_account(request):
    orders_count = request.user.orders.count()
    return render(request, 'my_account.html', {'orders_count': orders_count})

@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related('items__product').order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})
