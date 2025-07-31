from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem, Product
from .pagination import StandardResultsSetPagination
from .serializers import (AdjustCartItemSerializer, CartItemSerializer,
                          CartSerializer, OrderSerializer, ProductSerializer,
                          RemoveCartItemSerializer, UserSerializer)


@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products.
    - list, retrieve: Accessible by authenticated users (IsAuthenticated)
    - create, update, partial_update, destroy: Restricted to Admin users (IsAdminUser)
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["price", "stock"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "stock"]
    pagination_class = StandardResultsSetPagination
    lookup_field = "pk"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:  # 'list', 'retrieve'
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


@extend_schema(tags=["Carts"])
class CartViewSet(viewsets.ViewSet):
    """
    API endpoint for managing the authenticated user's cart.
    - retrieve: View user's cart.
    - add_item: Add product to cart.
    - remove_item: Remove product from cart or reduce quantity.
    All actions require authentication.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CartSerializer

    def get_cart(self):
        """Helper to get or create the user's cart."""
        cart, created = (
            Cart.objects.filter(user=self.request.user)
            .prefetch_related(
                Prefetch(
                    "cart_items", queryset=CartItem.objects.select_related("product_id")
                )
            )
            .get_or_create(user=self.request.user)
        )
        return cart

    @extend_schema(
        responses={200: CartSerializer},
        description="Retrieve the authenticated user's cart.",
        summary="Get User Cart",
    )
    def retrieve(self, request):
        """Retrieve the authenticated user's cart."""
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        request=CartItemSerializer,
        responses={200: CartSerializer},
        description="Add a product to the cart or update its quantity. If adding an existing product, it increments the quantity.",
        summary="Add or Update Cart Item",
    )
    def add_item(self, request):
        """Add a product to the cart or update its quantity. If adding an existing product, it increments the quantity."""
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if product.stock < quantity:
            return Response(
                {
                    "detail": f"Not enough stock for {product.name}. Available: {product.stock}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart()

        with transaction.atomic():
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart, product_id=product, defaults={"quantity": quantity}
            )
            if not item_created:
                new_quantity = cart_item.quantity + quantity
                if product.stock < new_quantity:
                    return Response(
                        {
                            "detail": f"Adding {quantity} more would exceed stock. Current cart: {cart_item.quantity}, Available: {product.stock}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

            cart = self.get_cart()
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AdjustCartItemSerializer,
        responses={200: CartSerializer},
        description="Adjusts the quantity of a product in the cart by incrementing or decrementing. Action can either be 'increment' or 'decrement'.",
        summary="Adjust Cart Item Quantity",
    )
    def adjust_item_quantity(self, request):
        """
        Adjusts the quantity of a product in the cart by incrementing or decrementing. Action can either be 'increment' or 'decrement'.
        """
        product_id = request.data.get("product_id")
        action = request.data.get("action")
        change_by = request.data.get("change_by", 1)

        serializer = AdjustCartItemSerializer(
            data={"product_id": product_id, "action": action, "change_by": change_by}
        )

        serializer.is_valid(raise_exception=True)

        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        product = cart_item.product_id

        with transaction.atomic():
            if action == "increment":
                new_quantity = cart_item.quantity + change_by
                if product.stock < new_quantity:
                    return Response(
                        {
                            "detail": f"Cannot increment. Not enough stock for {product.name}. Available: {product.stock}, Current cart: {cart_item.quantity}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                cart_item.quantity = new_quantity
                cart_item.save()
                message = (
                    f"Quantity of {product.name} incremented to {cart_item.quantity}."
                )
            elif action == "decrement":
                new_quantity = cart_item.quantity - change_by
                if new_quantity < 1:
                    # If decrementing would make quantity 0 or less, remove the item
                    cart_item.delete()
                    message = f"Product {product.name} removed from cart."
                else:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    message = f"Quantity of {product.name} decremented to {cart_item.quantity}."

            cart = self.get_cart()
            serializer = CartSerializer(cart)
            return Response(
                {"message": message, "cart": serializer.data}, status=status.HTTP_200_OK
            )

    @extend_schema(
        request=RemoveCartItemSerializer,
        responses={200: CartSerializer},
        summary="Remove a product from the cart entirely.",
        description="Remove a product from the cart entirely. This explicitly deletes the cart item",
    )
    def remove_item(self, request):
        """
        Removes a product from the cart entirely. This explicitly deletes the cart item.
        """
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

        with transaction.atomic():
            cart_item.delete()
            message = f"Product {cart_item.product_id.name} removed from cart."
            cart = self.get_cart()
            serializer = CartSerializer(cart)
            return Response(
                {"message": message, "cart": serializer.data}, status=status.HTTP_200_OK
            )

    @extend_schema(
        description="Clear all items from the user's cart",
        summary="Clear cart",
        responses={204: "No Content"},
    )
    def clear_cart(self, request):
        """Clear all items from the user's cart."""
        cart = self.get_cart()
        with transaction.atomic():
            cart.cart_items.all().delete()
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response({"detail": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Orders"])
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user orders.
    - create: Create an order from the cart.
    - list: List authenticated user's orders.
    - retrieve: Retrieve a single order by ID (user's own or any for admin).
    All actions require authentication.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    lookup_field = "pk"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:  # 'list', 'retrieve', 'create'
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns orders only for the authenticated user.
        Admin users can see all orders.
        """
        if self.request.user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """Create an order from the user's cart."""
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.cart_items.all()

        if not cart_items:
            return Response(
                {"detail": "Your cart is empty. Add items before placing an order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Check stock for all items before proceeding
            for item in cart_items:
                product = item.product_id
                if product.stock < item.quantity:
                    return Response(
                        {
                            "detail": f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {item.quantity}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            total_amount = sum(item.subtotal for item in cart_items)
            order = Order.objects.create(
                user=user, total_amount=total_amount, status="pending"
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product_id,
                    product_name=item.product_id.name,
                    quantity=item.quantity,
                    price_at_order=item.product_id.price,
                )
                item.product_id.reduce_stock(item.quantity)

            cart_items.delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Note: list and retrieve methods are provided by ModelViewSet automatically
    # We override get_queryset to handle user-specific vs. admin access for list/retrieve
