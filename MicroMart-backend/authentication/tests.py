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


class AuthTests(APITestCase):
    """
    Tests for user authentication (registration and login).
    """

    def setUp(self):
        self.register_url = reverse("user_register")
        self.login_url = reverse("user_login")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.client = APIClient()

    def test_user_registration_success_and_cart_creation(self):
        """
        Ensure a new user can successfully register and an empty cart is created.
        """
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(hasattr(user, "cart"))  # Check if cart exists for the user
        self.assertIsNotNone(user.cart)
        self.assertEqual(user.cart.cart_items.count(), 0)  # Cart should be empty

        # Verify tokens are returned on registration (as per your auth app's create method)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_registration_password_mismatch(self):
        """
        Ensure registration fails if passwords do not match.
        """
        data = self.user_data.copy()
        data["confirm_password"] = "differentpassword"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("password", response.data)
        self.assertEqual(User.objects.count(), 0)

    def test_user_registration_duplicate_username_or_email(self):
        """
        Ensure registration fails with a duplicate username or email.
        """
        # First registration
        self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(User.objects.count(), 1)

        # Attempt duplicate username
        duplicate_username_data = self.user_data.copy()
        duplicate_username_data["email"] = (
            "another@example.com"  # Change email to avoid email conflict
        )
        response = self.client.post(
            self.register_url, duplicate_username_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertEqual(User.objects.count(), 1)  # Still only one user

        # Attempt duplicate email
        duplicate_email_data = self.user_data.copy()
        duplicate_email_data["username"] = (
            "anotheruser"  # Change username to avoid username conflict
        )
        response = self.client.post(
            self.register_url, duplicate_email_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), 1)  # Still only one user

    def test_user_login_success_with_email_and_password(self):
        """
        Ensure a registered user can log in using their email and password.
        """
        # Register the user first
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """
        Ensure login fails with invalid credentials.
        """
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {"email": self.user_data["email"], "password": "wrongpassword"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", response.data)
