from django.db import models
from django.utils.text import slugify
import random
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ("Mobile Phones", "Mobile Phones"),
    ("Tablets", "Tablets"),
    ("Laptops", "Laptops"),
    ("Headphones", "Headphones"),
    ("Earbuds", "Earbuds"),
    ("Camera", "Camera"),
)


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    short_desc = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50)
    price = models.FloatField()
    discount = models.FloatField()
    available_quantity = models.IntegerField()
    image1 = models.ImageField(default="default.jpg", upload_to="product_images")
    image2 = models.ImageField(null=True, blank=True, upload_to="product_images")
    image3 = models.ImageField(null=True, blank=True, upload_to="product_images")
    image4 = models.ImageField(null=True, blank=True, upload_to="product_images")
    tags = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        value = self.product_name
        if not self.slug:
            self.slug = slugify(value, allow_unicode=True)
            check_slug = Product.objects.filter(slug=self.slug)
            if check_slug:
                self.slug += "-{num}".format(num=str(random.randrange(1, 100)))
        super().save(*args, **kwargs)


# Order Item -------
class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=10, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # product = models.IntegerField()
    quantity = models.IntegerField()
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name

    def total_cart_amount(self, *args, **kwargs):
        order_items = OrderItem.objects.filter(
            user=self.request.user, is_ordered=False
        ).all()
        total_amount = 0
        total_savings = 0
        for item in order_items:
            total_amount += item.quantity * (item.product.price - item.product.discount)
            total_savings += item.quantity * item.product.discount
        return total_amount, total_savings

    # def cart_savings(self, *args, **kwargs):


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255)
    zip_code = models.IntegerField()
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.line1


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=10)
    total_amount = models.FloatField(default=0)
    total_items = models.IntegerField()
    coupon = models.CharField(max_length=10, blank=True, null=True)
    coupon_amount = models.FloatField(default=0)
    order_amount = models.FloatField(default=0)
    savings = models.FloatField(default=0)
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)