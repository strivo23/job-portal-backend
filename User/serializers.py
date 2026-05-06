from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import userProfile


# ─────────────────────────────────────────────
# 1. USER PROFILE SERIALIZER (your existing code)
# ─────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = userProfile
        fields = [
            'user_type',
            'email',
            'phone_number',
        ]


# ─────────────────────────────────────────────
# 2. REGISTER SERIALIZER (your existing code)
# ─────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'profile',
        ]

    def get_profile(self, obj):
        """Get profile data from related userprofile object"""
        if hasattr(obj, 'userprofile'):
            return UserProfileSerializer(obj.userprofile).data
        return None

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def create(self, validated_data):
        validated_data.pop('profile', None)  # Remove profile from validated_data as it's a read-only field
        profile_data = self.initial_data.get('profile', {})
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        profile_data.setdefault('email', user.email)
        userProfile.objects.create(user=user, **profile_data)
        return user


# ─────────────────────────────────────────────
# 3. USER SERIALIZER (your existing code)
# ─────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile',
        ]

    def get_profile(self, obj):
        """Get profile data from related userprofile object"""
        if hasattr(obj, 'userprofile'):
            return UserProfileSerializer(obj.userprofile).data
        return None


# ─────────────────────────────────────────────
# 4. LOGIN SERIALIZER (new)
# Authenticates using username + password
# (Django's default User uses username, not email)
# ─────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        attrs['user'] = user  # passed to view via validated_data['user']
        return attrs


# ─────────────────────────────────────────────
# 5. CHANGE PASSWORD SERIALIZER (new)
# ─────────────────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):
    current_password    = serializers.CharField(write_only=True, required=True)
    new_password        = serializers.CharField(
                            write_only=True,
                            required=True,
                            validators=[validate_password],
                          )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError(
                {"confirm_new_password": "New passwords do not match."}
            )
        return attrs