from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
import random
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    GenericAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.decorators import parser_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONOpenAPIRenderer, JSONRenderer
from .pagination import CustomPagination
from .models import Product, OrderItem, Address, Order, Wishlist
from .serializers import (
    ProductSerializer,
    OrderItemSerializer,
    AddressSerializer,
    OrderSerializer,
    WishlistSerializer,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

# Product List
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)


# Product List Custom
class ProductListCustomView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter, )
    filter_fields = ('category',)
    ordering_fields = ('price',)
    search_fields = ('product_name', )


# Retrieve a Product
class ProductRetrieveView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = "slug"


# Create an Order Item
class CreateOrderItem(CreateAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = (IsAuthenticated,)


class AddToCartView(APIView):
    parser_classes = [JSONParser]
    renderer_classes = [JSONOpenAPIRenderer]
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        product = Product.objects.filter(slug=request.data.get("slug")).first()
        if product is None:
            return Response(
                {"error": "Product does not exist"}, status=HTTP_400_BAD_REQUEST
            )
        order_item = OrderItem.objects.filter(
            user=self.request.user, product=product, is_ordered=False
        ).first()
        quantity = int(request.data.get("quantity"))
        if order_item is not None:
            quantity += order_item.quantity
            if quantity > 5:
                return Response(
                    {"message": "Maximum quantity is limited to 5"},
                    status=HTTP_400_BAD_REQUEST,
                )
            order_item.quantity = quantity
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                user=request.user, product=product, quantity=quantity
            )
        serializer = OrderItemSerializer(order_item)
        return Response(data=serializer.data, status=HTTP_201_CREATED)


class UpdateOrderItemQuantityView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    lookup_field = "pk"

    def partial_update(self, request, pk):
        user = self.request.user
        order_item = OrderItem.objects.filter(pk=pk).first()

        if order_item is None:
            return Response(
                {"message": "Item is not present in Cart"}, status=HTTP_400_BAD_REQUEST
            )

        if user.id != order_item.user_id:
            return Response(
                {"message": "You do not have permission to update this item"},
                status=HTTP_403_FORBIDDEN,
            )

        if request.data.get("quantity") == 0:
            order_item.delete()
            return Response(status=HTTP_204_NO_CONTENT)

        instance = (
            self.get_object()
        )  # I think you can use this line if you lookup using primary key else follow below
        # serializer = OrderItemSerializer(instance=order_item, data=request.data, partial=True)

        print(request.data)
        serializer = OrderItemSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=HTTP_201_CREATED)
        return Response(data="Wrong Parameters", status=HTTP_400_BAD_REQUEST)


class RemoveFromCart(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()

    def destroy(self, request, pk):
        order_item = get_object_or_404(OrderItem, pk=pk)
        if order_item.user != request.user:
            return Response(
                {"message": "You do not have permission to delete this item"},
                status=HTTP_403_FORBIDDEN,
            )

        order_item.delete()
        return Response(status=HTTP_204_NO_CONTENT)


# List of items in cart ----
class CartItemsView(APIView):
    parser_classes = [JSONParser]
    renderer_classes = [JSONOpenAPIRenderer]
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderItemSerializer

    def get(self, request):
        cart_items_res = []
        cart_items = OrderItem.objects.filter(user=request.user, is_ordered=False).all()
        total_items = 0
        for item in cart_items:
            item_res = {
                "id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.product_name,
                "slug": item.product.slug,
                "price": item.product.price,
                "discount": item.product.discount,
                "quantity": item.quantity,
                "image": "http://" + request.META["HTTP_HOST"] + "/media/" + str(item.product.image1),
                "total_price": round(
                    item.quantity * (item.product.price - item.product.discount), 2
                ),
            }
            total_items += item.quantity
            cart_items_res.append(item_res)

        total_cart_amount, total_cart_savings = OrderItem.total_cart_amount(self)
        return Response(
            {
                "cartItems": cart_items_res,
                "cartTotal": round(total_cart_amount, 2),
                "cartSavings": round(total_cart_savings, 2),
                "cartCount": total_items,
            },
            status=HTTP_200_OK,
        )


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderView(APIView):
    parser_classes = [JSONParser]
    renderer_classes = [JSONOpenAPIRenderer]
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        order_id = "ODR{num}".format(num=str(random.randrange(100000, 1000000)))
        order_items = OrderItem.objects.filter(
            user=request.user, is_ordered=False
        ).all()

        if order_items is None:
            return Response(
                {"message": "There are no items in your cart"},
                status=HTTP_400_BAD_REQUEST,
            )

        total_cart_amount, total_cart_savings = OrderItem.total_cart_amount(self)

        item_count = 0;
        for item in order_items:
            item.is_ordered = True
            item.order_id = order_id
            item_count += item.quantity
            item.save()

        coupon_name = request.data.get("coupon")
        if coupon_name == "INSTANT10":
            coupon_amount = round(total_cart_amount * 0.1, 2)
        else:
            coupon_amount = 0

        address = Address.objects.get(pk=request.data.get("address_id"))
        order = Order.objects.create(
            user=request.user,
            order_id=order_id,
            total_amount=round(total_cart_amount + total_cart_savings, 2),
            total_items=item_count,
            coupon=request.data.get("coupon"),
            coupon_amount=coupon_amount,
            order_amount=round(total_cart_amount - coupon_amount, 2),
            savings=round(coupon_amount + total_cart_savings, 2),
            address=address,
        )
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=HTTP_201_CREATED)


class OrderRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]
    renderer_classes = [JSONOpenAPIRenderer]

    def get(self, request, order_id, *args, **kwargs):
        # order_id = request.data.get("order_id")
        order = Order.objects.filter(order_id=order_id, user=request.user).first()
        if order is None:
            return Response(
                {"message": "No matching orders found"}, status=HTTP_400_BAD_REQUEST
            )

        order_items = OrderItem.objects.filter(order_id=order_id).all()
        address = Address.objects.filter(pk=order.address.id)[0]

        order_items_res = []
        for item in order_items:
            item_res = {
                "id": item.id,
                "product_name": item.product.product_name,
                "slug": item.product.slug,
                "price": item.product.price,
                "discount": item.product.discount,
                "quantity": item.quantity,
                "image": "http://" + request.META["HTTP_HOST"] + "/media/" + str(item.product.image1),
                "total_price": item.quantity
                * (item.product.price - item.product.discount),
            }
            order_items_res.append(item_res)

        order_serializer = OrderSerializer(order)
        address_serializer = AddressSerializer(address)
        return Response(
            {
                "order": order_serializer.data,
                "order_items": order_items_res,
                "address": address_serializer.data,
            },
            status=HTTP_200_OK,
        )


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, pk):
        # if 1 != 2:
        #     return Response({"message": "User not same  111"})
        user = self.request.user
        wishlist = Wishlist.objects.filter(pk=pk).first()
        if wishlist is None:
            return Response(data={"message": "Item is not present in wishlist"}, status=HTTP_400_BAD_REQUEST)
        if user.id != wishlist.user_id:
            return Response(data={"message": "Not Authorized"}, status=HTTP_403_FORBIDDEN)
            # raise MyCustomExcpetion(detail={"message": "You are not the author of this blog"}, status_code=HTTP_403_FORBIDDEN)

        wishlist.delete()
        return Response(status=HTTP_204_NO_CONTENT)