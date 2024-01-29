from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from restaurant.models import Restaurant, Product, Cart, CartItem, OrderItem, Order
from .models import UserProfile


def owner_required(user):
    user_profile = UserProfile.objects.get(user=user)
    return user_profile.role == 'owner'


def user_required(user):
    user_profile = UserProfile.objects.get(user=user)
    return user_profile.role == 'user'


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = UserProfile.objects.create(user=user, role="user")
            user_profile.save()
            return redirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'base/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.user.role == "user":
                return redirect('restaurant')
            return redirect('edit_restaurant')
        else:
            return render(request, 'base/login.html', {'error': 'Nie poprawne dane logowania'})
    else:
        return render(request, 'base/login.html')


@login_required
def edit_restaurant(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role == "owner":
        restaurant = user_profile.owned_restaurant
        if request.method == "POST":
            form = RestaurantEditForm(request.POST, request.FILES, instance=restaurant)
            if form.is_valid():
                form.save()
                return redirect('edit_restaurant')
        else:
            form = RestaurantEditForm(instance=restaurant)
        return render(request, 'owner/edit_restaurant.html', {'form': form})
    else:
        return HttpResponseForbidden("You don't have permission to access this page")


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view, )
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'user/restaurant_list.html', {'restaurants': restaurants})


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view)
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    products = Product.objects.filter(restaurant=restaurant)
    cart, created = Cart.objects.get_or_create(user=request.user)

    context = {
        'restaurant': restaurant,
        'products': products,
        'cart': cart,
    }

    return render(request, 'user/restaurant_detail.html', context)


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.GET.get('quantity', 1))

    if quantity > product.quantity:
        return redirect(request.GET.get('next'))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = cart_item.quantity + quantity if not created else quantity
    cart_item.save()

    product.quantity -= quantity
    product.save()

    next = request.GET.get('next')
    return redirect(next)


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view)
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    quantity = int(request.POST.get('quantity', 1))
    if cart_item.quantity > quantity:
        cart_item.quantity -= quantity
        product.quantity += quantity
        product.save()
        cart_item.save()
    else:
        product.quantity += cart_item.quantity
        product.save()
        cart_item.delete()
    return redirect('cart')


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view)
def cart_view(request):
    user = request.user
    products = CartItem.objects.filter(cart__user=user)
    total = 0
    for i in products:
        total += i.total_price()
    return render(request, "user/cart.html", {'items': products, 'price': total})


@login_required(login_url=login_view)
def logout_view(request):
    logout(request)
    return redirect('login')


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'phone_number']


class RegisterRestaurantForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')



def register_restaurant(request):
    if request.method == 'POST':
        form = RegisterRestaurantForm(request.POST)
        restaurant_form = RestaurantForm(request.POST)
        if form.is_valid() and restaurant_form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            user_profile = UserProfile.objects.create(user=user, role="owner")
            restaurant = restaurant_form.save(commit=False)
            restaurant.save()
            user_profile.owned_restaurant = restaurant
            user_profile.save()
            login(request, user)
            return redirect('login')
    else:
        form = RegisterRestaurantForm()
        restaurant_form = RestaurantForm()
    return render(request, 'base/restaurant_register.html', {'form': form, 'restaurant_form': restaurant_form})


class RestaurantEditForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'phone_number', 'image']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity']


@user_passes_test(owner_required, login_url=restaurant_list)
@login_required(login_url=login_view)
def manage_products(request):
    user_profile = UserProfile.objects.get(user=request.user)
    restaurant = user_profile.owned_restaurant
    if request.user.user.owned_restaurant != restaurant:
        return redirect('forbidden')
    products = Product.objects.filter(restaurant=restaurant)
    return render(request, 'owner/manage_products.html', {'restaurant': restaurant, 'products': products})


@user_passes_test(owner_required, login_url=restaurant_list)
@login_required(login_url=login_view)
def add_product(request):
    user_profile = UserProfile.objects.get(user=request.user)
    restaurant = user_profile.owned_restaurant
    if user_profile.role != 'owner' or request.user.user.owned_restaurant != restaurant:
        return redirect('forbidden')
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        Product.objects.create(restaurant=restaurant, name=name, quantity=quantity, price=price)
        return redirect('add_product')
    return render(request, 'user/add_product.html', {'restaurant': restaurant})


@user_passes_test(owner_required, login_url=restaurant_list)
@login_required(login_url=login_view)
def edit_product(request, product_id):
    user_profile = UserProfile.objects.get(user=request.user)
    restaurant = user_profile.owned_restaurant
    if request.user.user.owned_restaurant != restaurant:
        return redirect('forbidden')
    product = get_object_or_404(Product, id=product_id, restaurant=restaurant)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('edit_product', product_id=product_id)
    return render(request, 'owner/edit_product.html', {'form': form, 'restaurant': restaurant})


@user_passes_test(owner_required, login_url=restaurant_list)
@login_required(login_url=login_view)
def delete_product(request, product_id):
    user_profile = UserProfile.objects.get(user=request.user)
    restaurant = user_profile.owned_restaurant
    if request.user.user.owned_restaurant != restaurant:
        return redirect('forbidden')
    product = get_object_or_404(Product, id=product_id, restaurant=restaurant)
    product.delete()
    return


@user_passes_test(user_required, login_url=edit_restaurant)
@login_required(login_url=login_view)
def order_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('cart')
    restaurants = set(item.restaurant for item in cart.products.all())
    for restaurant in restaurants:
        order = Order.objects.create(user=request.user, restaurant=restaurant)
        for item in cart.cartitem_set.filter(product__restaurant=restaurant):
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
    cart.delete()
    return redirect('cart')



@method_decorator(user_passes_test(user_required, login_url=edit_restaurant), name='dispatch')
@method_decorator(login_required(login_url=login_view), name='dispatch')
class OrderHistoryView(ListView):
    model = Order
    template_name = 'user/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)




@method_decorator(user_passes_test(owner_required, login_url=restaurant_list), name='dispatch')
@method_decorator(login_required(login_url=login_view), name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'owner/orders.html'

    def get_queryset(self):
        restaurant = UserProfile.objects.get(user=self.request.user).owned_restaurant
        return Order.objects.filter(restaurant=restaurant)


@method_decorator(user_passes_test(owner_required, login_url=restaurant_list), name='dispatch')
@method_decorator(login_required(login_url=login_view), name='dispatch')
def update_status(request, order_id):
    order = Order.objects.get(id=order_id)
    restaurant = order.restaurant

    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()

    return redirect("Order")
