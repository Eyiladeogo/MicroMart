from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    This serializer is used to serialize user data for API responses.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username"]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    This serializer is used to validate user sign up details.
    It requires a username, email, password, and confirmation password.
    """

    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        # Validate data passed in by user
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        # Check if the email is already registered
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        # Check if the username is already taken
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {"username": "A user with this username already exists."}
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")

        # Create user instance
        try:
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "A user with this username or email already exists."}
            )
        except Exception as e:
            raise serializers.ValidationError(
                {
                    "detail": "Could not complete user registration due to an internal error."
                }
            )

    def update(self, validated_data):
        pass


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for user login.
    This serializer is used to validate user login details and generate tokens.
    """

    User = get_user_model()

    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)

    password = serializers.CharField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        """
        Overrides the serializer's initialization to customize its fields.
        """
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields.pop(
                "username"
            )  # This is to ensure compatibility with the base TokenObtainPairSerializer

        # Explicitly redefine the fields we want to use
        self.fields["username"] = serializers.CharField(write_only=True, required=False)
        self.fields["email"] = serializers.EmailField(write_only=True, required=False)
        self.fields["password"] = serializers.CharField(write_only=True, required=True)

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, data):
        username_input = data.get("username", None)
        email_input = data.get("email", None)
        password_input = data.get("password")

        if not (username_input or email_input):
            raise serializers.ValidationError(
                {"detail": 'Must provide either "username" or "email"'}
            )
        if username_input and email_input:
            raise serializers.ValidationError(
                {"detail": 'Cannot provide both "username" and "email"'}
            )

        # Attempt to find the user by username or email
        user = None
        if username_input:
            try:
                user = self.User.objects.filter(username=username_input).first()
            except self.User.DoesNotExist:
                pass
        elif email_input:
            try:
                user = self.User.objects.filter(email=email_input).first()
            except self.User.DoesNotExist:
                pass

        if user is None or not user.check_password(password_input):
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials"},
                code="authentication_failed",
            )

        # Pass the data back to the parent class for validation
        data[self.username_field] = user.username

        if email_input:
            del data["email"]  # Parent class doesnt expect email field

        data = super().validate(data)

        if self.user:
            self.user.last_login = timezone.now()
            self.user.save(update_fields=["last_login"])

        return data
