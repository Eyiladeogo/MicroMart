from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import UserLoginViewSet, UserProfileViewSet, UserRegistrationViewSet

urlpatterns = [
    # Path for user registration
    path(
        "register/",
        UserRegistrationViewSet.as_view({"post": "create"}),
        name="user_register",
    ),
    # Path for user login
    path("login/", UserLoginViewSet.as_view({"post": "create"}), name="user_login"),
    # Path to retrieve user profile
    path(
        "profile/", UserProfileViewSet.as_view({"get": "retrieve"}), name="user_profile"
    ),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Path to refresh an expired access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Path to verify a token (useful for debugging or client-side checks)
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
