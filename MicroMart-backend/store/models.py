from authentication.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """
    Represents a product available in the store.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(1.00)]
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        """Reduces the product stock by the given quantity."""
        if self.stock < quantity:
            raise ValueError("Not enough stock available.")
        self.stock -= quantity
        self.save()

    def increase_stock(self, quantity):
        """Increases the product stock by the given quantity."""
        self.stock += quantity
        self.save()


class Cart(models.Model):
    """
    Represents a user's shopping cart.
    One-to-one relationship with the User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        """Calculates the total number of items in the cart."""
        return self.cart_items.aggregate(total=models.Sum("quantity"))["total"] or 0

    @property
    def total_amount(self):
        """Calculates the total monetary amount of items in the cart."""
        return sum(item.subtotal for item in self.cart_items.all())


class CartItem(models.Model):
    """
    Represents an individual item within a shopping cart.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "cart",
            "product_id",
        )  # A product can only appear once per cart
        ordering = ["product_id__name"]

    def __str__(self):
        return f"{self.quantity} x {self.product_id.name} in {self.cart.user.username}'s cart"

    @property
    def subtotal(self):
        """Calculates the subtotal for this cart item."""
        return self.quantity * self.product_id.price


class Order(models.Model):
    """
    Represents a placed order.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Order by most recent orders first

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    """
    Represents an individual item within an order.
    Stores the product details at the time of order to maintain historical accuracy.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_order = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)]
    )  # Price at the time of order

    class Meta:
        unique_together = (
            "order",
            "product",
        )  # A product can only appear once per order
        ordering = ["product_name"]

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order {self.order.id}"
