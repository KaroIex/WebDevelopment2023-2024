from django.db import models
from django.contrib.auth.models import User
from django.views.generic import CreateView


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product-img/', null=True, blank=True)

    def photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    ROLES = [
        ("user", "user"),
        ("owner", "owner"),
    ]
    role = models.CharField(max_length=255, choices=ROLES)
    owned_restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.user) + " " + "profile"


class Product(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    date = models.DateTimeField(auto_now_add=True)
    STATUS = [
        ("nowe", "nowe"),
        ("w trakcie", "w trakcie"),
        ("gotowe", "gotowe"),
        ("wysłane", "wysłane"),
    ]
    status = models.CharField(max_length=255, choices=STATUS, default='nowe')

    def total_price(self):
        total = 0
        for item in self.orderitem_set.all():
            total += item.product.price * item.quantity
        return total

    def __str__(self):
        return str(self.user) + " order " + str(self.date)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.order) + ": " + str(self.product) + " x " + str(self.quantity)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def total_price(self):
        total = 0
        for item in self.cartitem_set.all():
            total += item.product.price * item.quantity
        return total

    def __str__(self):
        return str(self.user) + " cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.cart) + ": " + str(self.product) + " x " + str(self.quantity)
