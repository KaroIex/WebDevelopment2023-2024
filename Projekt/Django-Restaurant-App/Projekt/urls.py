from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from Projekt import settings
from restaurant.views import register, login_view, restaurant_list, restaurant_detail, add_to_cart, cart_view, \
    logout_view, remove_from_cart, register_restaurant, edit_restaurant, manage_products, add_product, edit_product, \
    delete_product, add_product, order_cart, OrderHistoryView, OrderListView, update_status

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', login_view, name='login'),
                  path('register/', register, name='register'),
                  path('login/', login_view, name='login'),
                  path('restaurant/', restaurant_list, name='restaurant'),
                  path('restaurant/<int:restaurant_id>/', restaurant_detail, name='restaurant_detail'),
                  path('add/to/cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
                  path('cart/', cart_view, name='cart'),
                  path('logout/', logout_view, name='logout'),
                  path('remove/from/cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
                  path('register/restaurant/', register_restaurant, name='register_restaurant'),
                  path('edit/restaurant/', edit_restaurant, name='edit_restaurant'),
                  path('manage/products/', manage_products, name='manage_products'),
                  path('edit/product/<int:product_id>/', edit_product, name='edit_product'),
                  path('delete/product/<int:product_id>/', delete_product, name='delete_product'),
                  path('add/product/', add_product, name='add_product'),
                  path('order/cart/', order_cart, name='order_cart'),
                  path('order/history/', OrderHistoryView.as_view(), name='order_history'),
                  path('order/restaurant', OrderListView.as_view(), name='Order'),
                  path('update/status/<int:order_id>', update_status, name='update_status'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
