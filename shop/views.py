from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem, Order
from django.db import transaction

def home(request):
    """Simple home page with featured products"""
    featured_products = Product.objects.filter(stock__gt=0).order_by('?')[:4]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    """List all products"""
    products = Product.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    """Show product details"""
    product = get_object_or_404(Product, id=product_id)
    
    context = {
        'product': product,
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def cart_view(request):
    """Display user's active cart"""
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    
    context = {
        'cart': cart,
        'items': cart.items.all(),
    }
    return render(request, 'shop/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect('product_detail', product_id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated {product.name} quantity to {cart_item.quantity}")
        else:
            messages.warning(request, f"Cannot add more {product.name}. Only {product.stock} left.")
    else:
        messages.success(request, f"Added {product.name} to cart")
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    # Ensure we only remove from active carts
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user, cart__is_active=True)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"Removed {product_name} from cart")
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        # Ensure we only update active carts
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user, cart__is_active=True)
        
        if quantity > 0:
            if quantity <= cart_item.product.stock:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"Updated quantity to {quantity}")
            else:
                 messages.warning(request, f"Only {cart_item.product.stock} available in stock.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart")
    
    return redirect('cart')

@login_required
def checkout(request):
    """Checkout process with stock management"""
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        
        if not shipping_address:
            messages.error(request, "Please provide a shipping address")
            return render(request, 'shop/checkout.html', {'cart': cart})
        
        if cart.items.count() == 0:
            messages.error(request, "Your cart is empty")
            return redirect('cart')
        
        # Verify stock before processing
        for item in cart.items.all():
            if item.quantity > item.product.stock:
                messages.error(request, f"Not enough stock for {item.product.name}. Only {item.product.stock} available.")
                return redirect('cart')

        with transaction.atomic():
            # Decrement stock
            for item in cart.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                shipping_address=shipping_address,
                status='pending'
            )
            
            # Mark cart as inactive so user gets a new one next time
            cart.is_active = False
            cart.save()
            
        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'shop/checkout.html', {'cart': cart})

@login_required
def order_list(request):
    """List user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """Show order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)

def register(request):
    """Simple user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'shop/register.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'shop/login.html')

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')