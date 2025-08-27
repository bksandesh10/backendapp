from rest_framework import serializers
from .models import AuthUser, UserProfile


# --- Serializer for User Signup ---
class AuthUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = AuthUser(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user


# --- Serializer for User Profile ---
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'DOB', 'phone', 'profile_pic']


# --- Serializer for User with Profile (optional combined) ---
class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password')

        user = AuthUser(**validated_data)
        user.set_password(password)
        user.save()

        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)

        return user
