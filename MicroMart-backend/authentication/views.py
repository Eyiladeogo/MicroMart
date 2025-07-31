from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenBlacklistView

from store.models import Cart

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegistrationSerializer,
    UserSerializer,
)


@extend_schema(tags=["Authentication"])
class UserRegistrationViewSet(GenericViewSet, CreateModelMixin):
    """
    ViewSet for user registration.
    This allows users to register by providing a username, email, and password.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.all()

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Automatically create a cart for the new user
        Cart.objects.create(user=user)

        # Generate token
        token_serializer = TokenObtainPairSerializer(
            data={
                "username": user.username,
                "password": serializer.validated_data["password"],
            }
        )
        token_serializer.is_valid(raise_exception=True)
        tokens = token_serializer.validated_data

        # Prepare response data
        response_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Authentication"])
class UserLoginViewSet(GenericViewSet, CreateModelMixin):
    """
    ViewSet for user login.
    This allows users to log in by providing their username/email and password.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    ViewSet for user profile management.
    This allows users to view and update their profile information.
    """

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
