from rest_framework import serializers
from .models import Product, OrderItem, Address, Order, Wishlist
from django.conf import settings


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        # lookup_field = "slug"


class OrderItemSerializer(serializers.ModelSerializer):
    product_obj = ProductSerializer(required=False, read_only=True)

    class Meta:
        model = OrderItem
        # fields = ["id", "user", "order_id", "product", "product_obj", "quantity", "is_ordered", "created_at"]
        fields = "__all__"

    # def create(self, validated_data):
    #     order_item = OrderItem()
    #     slug = validated_data["slug"]
    #     product = Product.objects.filter(slug=slug).first()
    #     order_item.product = product
    #     order_item.user = self.request.user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "first_name",
            "last_name",
            "line1",
            "line2",
            "landmark",
            "zip_code",
            "state",
            "country",
            "mobile",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField("get_product_image")
    product_detail = serializers.SerializerMethodField("get_product_detail")

    def get_product_image(self, wishlist):
        return settings.DOMAIN_NAME + "/media/" + str(wishlist.product.image1)

    def get_product_detail(self, wishlist):
        product = wishlist.product
        return ProductSerializer(product).data

    class Meta:
        model = Wishlist
        fields = ["id", "product", "product_image", "product_detail"]