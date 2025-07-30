from django.urls import path
from rest_framework_simplejwt.views import (TokenBlacklistView,
                                            TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from .views import (UserLoginViewSet, UserProfileViewSet,
                    UserRegistrationViewSet)

urlpatterns = [
    # Path for user registration
    path(
        "register/",
        UserRegistrationViewSet.as_view({"post": "create"}),
        name="user_register",
    ),
    # Path for user login
    path("login/", UserLoginViewSet.as_view({"post": "create"}), name="user_login"),
    path(
        "profile/", UserProfileViewSet.as_view({"get": "retrieve"}), name="user_profile"
    ),
    path(
        "profile/update/",
        UserProfileViewSet.as_view({"patch": "update"}),
        name="user_profile_update",
    ),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Path to get a new access token and refresh token (for login)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Path to refresh an expired access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Path to verify a token (useful for debugging or client-side checks)
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
