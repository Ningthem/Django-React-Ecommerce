from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .api import (
    ProductListView,
    ProductListCustomView,
    ProductRetrieveView,
    CreateOrderItem,
    AddToCartView,
    RemoveFromCart,
    UpdateOrderItemQuantityView,
    CartItemsView,
    AddressViewSet,
    OrderView,
    OrderRetrieveView,
    OrderListView,
    WishlistViewSet
)

router = DefaultRouter()
router.register('', AddressViewSet, "address")

router_wishlist = DefaultRouter()
router_wishlist.register('', WishlistViewSet, "wishlist")

urlpatterns = [
    path('api/address/', include(router.urls)),
    path('api/wishlist/', include(router_wishlist.urls)),
    path('api/products/', ProductListView.as_view(), name="product_list"),
    path('api/products-filter/', ProductListCustomView.as_view(), name="product_list-custom"),
    path('api/products/<slug:slug>/', ProductRetrieveView.as_view(), name="product_list"),
    path('api/add-to-cart/', AddToCartView.as_view(), name="add_to_cart"),
    path('api/remove-from-cart/<pk>/', RemoveFromCart.as_view(), name="remove_from_cart"),
    path('api/order-item/change-quantity/<pk>/', UpdateOrderItemQuantityView.as_view(), name="update_order_item"),
    path('api/cart-items/', CartItemsView.as_view(), name="cart_items"),
    path('api/order/', OrderView.as_view(), name="order"),
    path('api/order/<str:order_id>/', OrderRetrieveView.as_view(), name="order_retrieve"),
    path('api/all-orders/', OrderListView.as_view(), name="order_list"),

]

# urlpatterns += router.urls