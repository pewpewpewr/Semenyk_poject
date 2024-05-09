from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.http import HttpResponse
from .models import Clothing, CartItem, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .models import Order

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('list_clothing')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list_clothing')
        else:
            return HttpResponse("Неправильний логін або пароль.")
    else:
        return render(request, 'core/login.html')


def list_clothing(request):
    categories = Clothing.objects.values_list('category', flat=True).distinct()
    category = request.GET.get('category', None)

    if category:
        clothing_list = Clothing.objects.filter(category=category)
    else:
        clothing_list = Clothing.objects.all()

    return render(request, 'core/clothing_list.html', {
        'clothing_list': clothing_list,
        'categories': categories,
        'current_category': category
    })

def clothing_detail(request, pk):
    clothing = get_object_or_404(Clothing, pk=pk)
    return render(request, 'core/clothing_detail.html', {'clothing': clothing})

def add_to_cart(request, clothing_id):
    clothing = get_object_or_404(Clothing, id=clothing_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, clothing=clothing)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, clothing_id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = 0

    items = []
    for item in cart_items:
        total = item.clothing.price * item.quantity
        total_price += total
        items.append({
            'id': item.clothing.id,
            'name': item.clothing.name,
            'quantity': item.quantity,
            'price': item.clothing.price,
            'total_price': total,
        })

    context = {
        'cart_items': items,
        'total_price': total_price
    }
    return render(request, 'core/cart_detail.html', context)

def list_clothing(request):
    category = request.GET.get('category', None)

    if category and category != "":
        clothing_list = Clothing.objects.filter(category=category)
    else:
        clothing_list = Clothing.objects.all() 

    return render(request, 'core/clothing_list.html', {
        'clothing_list': clothing_list,
        'current_category': category
    })

    
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'core/view_orders.html', {'orders': orders})

def display_clothes_for_purchase(request):
    clothes = Clothing.objects.all()
    return render(request, 'core/clothes_for_purchase.html', {'clothes': clothes})


@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return render(request, 'core/empty_cart.html', {'message': 'Ваша корзина порожня.'})

    order = Order.objects.create(user=request.user, total_price=0)
    total_price = 0

    for item in cart_items:
        total_item_price = item.clothing.price * item.quantity
        total_price += total_item_price
        OrderItem.objects.create(
            order=order,
            product=item.clothing,
            quantity=item.quantity,
            price=item.clothing.price
        )

    order.total_price = total_price
    order.save()

    cart_items.delete()

    return redirect('order_confirmation', order.id)

def order_confirmation(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    
    return render(request, 'core/order_confirmation.html', {'order': order})
