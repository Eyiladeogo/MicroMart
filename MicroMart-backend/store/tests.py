from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import (
    get_user_model,
)
from store.models import Product, Cart, CartItem, Order, OrderItem
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class ProductTests(APITestCase):
    """
    Tests for product management (listing, detail, admin CRUD) with updated permissions.
    """

    def setUp(self):
        self.client = APIClient()
        self.product_list_url = reverse("product-list")

        self.user = User.objects.create_user(
            username="testuser", email="user@example.com", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        self.product1 = Product.objects.create(
            name="Laptop",
            description="Powerful laptop",
            price=1200.00,
            stock=50,
            image="http://example.com/laptop.jpg",
        )
        self.product2 = Product.objects.create(
            name="Mouse",
            description="Wireless mouse",
            price=25.00,
            stock=200,
            image="http://example.com/mouse.jpg",
        )

        # Get authenticated clients
        self.user_client = self._get_auth_client(self.user.email, "password123")
        self.admin_client = self._get_auth_client(
            self.admin_user.email, "adminpassword"
        )

    def _get_auth_client(self, email, password):
        """Helper to get an authenticated client with JWT token."""
        client = APIClient()
        login_data = {"email": email, "password": password}
        response = client.post(reverse("user_login"), login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        return client

    def test_product_list_unauthenticated_access_forbidden(self):
        """
        Ensure unauthenticated users cannot view the product list.
        """
        response = self.client.get(self.product_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_list_authenticated_access(self):
        """
        Ensure authenticated users can view the product list.
        """
        response = self.user_client.get(self.product_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_product_list_filtering_and_pagination(self):
        """
        Test product list filtering by price and search by name, and pagination.
        """
        # Test filtering by price (authenticated user)
        response = self.user_client.get(
            self.product_list_url + "?price=1200.00", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Laptop")

        # Test search by name (authenticated user)
        response = self.user_client.get(
            self.product_list_url + "?search=mouse", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Mouse")

        response = self.user_client.get(
            self.product_list_url + "?page_size=1&page=1", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("next", response.data)  # Should have a 'next' link if more pages

    def test_product_detail_unauthenticated_access_forbidden(self):
        """
        Ensure unauthenticated users cannot view product details.
        """
        response = self.client.get(
            reverse("product-detail", args=[self.product1.id]), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_detail_authenticated_access(self):
        """
        Ensure authenticated users can view product details.
        """
        response = self.user_client.get(
            reverse("product-detail", args=[self.product1.id]), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")

    def test_admin_create_product_success(self):
        """
        Ensure admin can create a product.
        """
        new_product_data = {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 75.00,
            "stock": 100,
            "image": "http://example.com/keyboard.jpg",
        }
        response = self.admin_client.post(
            self.product_list_url, new_product_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(Product.objects.get(name="Keyboard").stock, 100)

    def test_non_admin_create_product_forbidden(self):
        """
        Ensure non-admin user cannot create a product.
        """
        new_product_data = {
            "name": "Monitor",
            "description": "4K Monitor",
            "price": 300.00,
            "stock": 30,
            "image": "http://example.com/monitor.jpg",
        }
        response = self.user_client.post(
            self.product_list_url, new_product_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 2)  # No new product created

    def test_unauthenticated_create_product_unauthorized(self):
        """
        Ensure unauthenticated user cannot create a product.
        """
        new_product_data = {
            "name": "Webcam",
            "description": "HD Webcam",
            "price": 50.00,
            "stock": 50,
            "image_url": "http://example.com/webcam.jpg",
        }
        response = self.client.post(
            self.product_list_url, new_product_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 2)  # No new product created


class CartTests(APITestCase):
    """
    Tests for shopping cart functionality.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="user@example.com", password="password123"
        )
        self.cart, _ = Cart.objects.get_or_create(user=self.user)

        self.product1 = Product.objects.create(
            name="Laptop",
            description="Powerful laptop",
            price=1200.00,
            stock=10,
            image="http://example.com/laptop.jpg",
        )
        self.product2 = Product.objects.create(
            name="Mouse",
            description="Wireless mouse",
            price=25.00,
            stock=5,
            image="http://example.com/mouse.jpg",
        )

        # Get authenticated client for the user
        self.auth_client = self._get_auth_client(self.user.email, "password123")

        # Cart URLs (from store.urls)
        self.add_to_cart_url = reverse("cart")
        self.cart_view_url = reverse("cart")  # For retrieving the cart

    def _get_auth_client(self, email, password):
        """Helper to get an authenticated client with JWT token."""
        client = APIClient()
        login_data = {"email": email, "password": password}
        response = client.post(reverse("user_login"), login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        return client

    def test_add_item_to_cart_success(self):
        """
        Ensure items can be added to the cart successfully.
        """
        data = {"product_id": self.product1.id, "quantity": 2}
        response = self.auth_client.post(self.add_to_cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.cart_items.count(), 1)
        cart_item = self.cart.cart_items.first()
        self.assertEqual(cart_item.product_id, self.product1)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(float(response.data["total_amount"]), 2400.00)  # 2 * 1200.00

        # Verify stock is NOT deducted at this stage (deducted on order creation)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 10)  # Should still be 10

    def test_add_existing_item_to_cart_updates_quantity(self):
        """
        Ensure adding an existing item to the cart updates its quantity.
        """
        CartItem.objects.create(cart=self.cart, product_id=self.product1, quantity=1)
        data = {"product_id": self.product1.id, "quantity": 2}
        response = self.auth_client.post(self.add_to_cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.cart.cart_items.count(), 1
        )  # Still one item, but quantity updated
        cart_item = self.cart.cart_items.first()
        self.assertEqual(cart_item.quantity, 3)  # 1 (initial) + 2 (added) = 3
        self.assertEqual(float(response.data["total_amount"]), 3600.00)  # 3 * 1200.00

    def test_add_item_out_of_stock_failure(self):
        """
        Ensure adding an item that's out of stock (or exceeds stock) fails.
        """
        data = {"product_id": self.product1.id, "quantity": 15}  # Product1 stock is 10
        response = self.auth_client.post(self.add_to_cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough stock", response.data["detail"])
        self.assertEqual(self.cart.cart_items.count(), 0)  # No item should be added

    def test_add_item_exceeds_stock_on_update_failure(self):
        """
        Ensure updating quantity of an existing item fails if it exceeds stock.
        """
        CartItem.objects.create(
            cart=self.cart, product_id=self.product1, quantity=8
        )  # 8 in cart, 10 stock
        data = {
            "product_id": self.product1.id,
            "quantity": 3,
        }  # Add 3 more, total 11 (exceeds 10)
        response = self.auth_client.post(self.add_to_cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exceed stock", response.data["detail"])
        self.assertEqual(
            self.cart.cart_items.first().quantity, 8
        )  # Quantity should not have changed

    def test_add_item_unauthenticated_unauthorized(self):
        """
        Ensure unauthenticated user cannot add items to cart.
        """
        data = {"product_id": self.product1.id, "quantity": 1}
        response = self.client.post(self.add_to_cart_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.cart.cart_items.count(), 0)  # No item added
