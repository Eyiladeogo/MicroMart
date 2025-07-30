from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Cart, CartItem, Order, OrderItem, Product
from .serializers import (CartItemSerializer, CartSerializer, OrderSerializer,
                          ProductSerializer, UserSerializer)


# --- Custom Pagination ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# --- Authentication Views ---
class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows anyone to create a new user account.
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Create an empty cart for the new user
        Cart.objects.create(user=user)
        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,  # Return user data without password
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view.
    Uses the default Simple JWT serializer.
    """

    permission_classes = (AllowAny,)


# --- Product Views ---
class ProductListView(generics.ListAPIView):
    """
    API endpoint for listing and searching products.
    Allows filtering by name/description and ordering by price/name.
    Anyone can view products.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["price", "stock"]  # Example: /products/?price=10.00
    search_fields = ["name", "description"]  # Example: /products/?search=shirt
    ordering_fields = ["name", "price", "stock"]  # Example: /products/?ordering=-price
    pagination_class = StandardResultsSetPagination


class ProductDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single product by ID.
    Anyone can view product details.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    lookup_field = "pk"  # Default lookup field is 'pk' (primary key)


# --- Admin Product Management Views ---
class ProductAdminViewSet(generics.ModelViewSet):
    """
    API endpoint for admin users to create, retrieve, update, and delete products.
    Only accessible by admin users.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminUser,)  # Only admin users can access this
    lookup_field = "pk"


# --- Cart Views ---
class CartView(generics.RetrieveAPIView):
    """
    API endpoint for viewing the authenticated user's cart.
    Authenticated users can view their own cart.
    """

    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Retrieves the cart for the current authenticated user.
        Creates a new cart if one doesn't exist for the user.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(APIView):
    """
    API endpoint for adding a product to the authenticated user's cart.
    Handles adding new items or updating quantity of existing items.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(quantity, int) or quantity < 1:
            return Response(
                {"detail": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        cart, created = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={"quantity": quantity}
            )
            if not item_created:
                # If item already exists, update quantity
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

            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCartView(APIView):
    """
    API endpoint for removing a product from the authenticated user's cart
    or reducing its quantity.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity_to_remove = request.data.get(
            "quantity", None
        )  # If None, remove all of this item

        if not product_id:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = get_object_or_404(Cart, user=request.user)

        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Product not found in cart."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            if quantity_to_remove is None or quantity_to_remove >= cart_item.quantity:
                # Remove the entire item
                cart_item.delete()
                message = "Product removed from cart."
            elif quantity_to_remove < cart_item.quantity and quantity_to_remove > 0:
                # Reduce quantity
                cart_item.quantity -= quantity_to_remove
                cart_item.save()
                message = f"Quantity of {cart_item.product.name} reduced."
            else:
                return Response(
                    {
                        "detail": "Quantity to remove must be a positive integer or not provided to remove all."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CartSerializer(cart)
            return Response(
                {"message": message, "cart": serializer.data}, status=status.HTTP_200_OK
            )


# --- Order Views ---
class OrderCreateView(generics.CreateAPIView):
    """
    API endpoint for creating an order from the user's cart.
    Requires authentication.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
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
                product = item.product
                if product.stock < item.quantity:
                    return Response(
                        {
                            "detail": f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {item.quantity}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Calculate total amount and create the order
            total_amount = sum(item.subtotal for item in cart_items)
            order = Order.objects.create(
                user=user, total_amount=total_amount, status="pending"
            )

            # Create order items and deduct stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price_at_order=item.product.price,
                )
                # Deduct stock
                item.product.reduce_stock(item.quantity)  # Using the model method

            # Clear the cart after order is placed
            cart_items.delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """
    API endpoint for listing authenticated user's orders.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Returns orders only for the authenticated user.
        Admin users can see all orders (handled by a separate view if needed, or by modifying this one).
        """
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single order by ID.
    Users can only view their own orders. Admin users can view any order.
    """

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "pk"

    def get_queryset(self):
        """
        Ensures a user can only retrieve their own orders.
        Admin users can access all orders.
        """
        if self.request.user.is_staff:  # is_staff implies admin access for this context
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
