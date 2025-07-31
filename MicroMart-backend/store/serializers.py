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

    product_name = serializers.CharField(source="product_id.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product_id.price", max_digits=10, decimal_places=2, read_only=True
    )
    product_image = serializers.ImageField(source="product_id.image", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "product_price",
            "product_image",
            "quantity",
            "subtotal",
        )
        read_only_fields = (
            "cart",
        )  # Cart is set by the view, not directly by user input

        def validate_quantity(self, value):
            """
            Validates that quantity is a positive integer.
            """
            if not isinstance(value, int) or value <= 0:
                raise serializers.ValidationError(
                    "Quantity must be a positive integer."
                )
            return value


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


class AdjustCartItemSerializer(serializers.Serializer):
    """
    Serializer for adjusting cart item quantity.
    Used for adding/removing items from the cart.
    """

    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    action = serializers.ChoiceField(choices=["increment", "decrement"])
    change_by = serializers.IntegerField(default=1, min_value=1)

    def validate(self, data):
        if data["action"] not in ["increment", "decrement"]:
            raise serializers.ValidationError(
                "Action must be 'increment' or 'decrement'."
            )
        if not isinstance(data["change_by"], int) or data["change_by"] < 1:
            raise serializers.ValidationError("Change by must be a positive integer.")
        return data


class RemoveCartItemSerializer(serializers.Serializer):
    """
    Serializer for removing an item from the cart.
    Used when a user wants to remove a specific item from their cart.
    """

    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())


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
