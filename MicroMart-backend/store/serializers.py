from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem, Product


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User registration.
    Ensures password is write-only and hashed.
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, data):
        """
        Validates that passwords match and username/email are unique.
        """
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {"username": "A user with that username already exists."}
            )
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "A user with that email already exists."}
            )
        return data

    def create(self, validated_data):
        """
        Creates a new user with hashed password.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """

    class Meta:
        model = Product
        fields = "__all__"  # Include all fields from the Product model


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    Includes product details for display.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "subtotal",
        )
        read_only_fields = (
            "cart",
        )  # Cart is set by the view, not directly by user input


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model.
    Includes nested CartItemSerializer to show cart contents.
    """

    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "cart_items",
            "total_items",
            "total_amount",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user",)  # User is set by the view


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "price_at_order")
        read_only_fields = (
            "order",
            "product_name",
            "price_at_order",
        )  # These are set during order creation


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    Includes nested OrderItemSerializer to show order details.
    """

    order_items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "user_username",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
            "order_items",
        )
        read_only_fields = (
            "user",
            "total_amount",
            "status",
        )  # These are set by the system
