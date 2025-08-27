from rest_framework import generics, permissions
from .models import AuthUser, UserProfile ,TempUser
from .serializers import  UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
import secrets
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError  
from django.utils.timezone import now, timedelta



class UserSignupView(APIView):
    permission_classes = []  # Allow anyone

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        # Check required fields
        if not email or not username or not password:
            return Response(
                {"status": "error", "message": "Email, username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"status": "error", "message": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if TempUser exists
        temp_user = TempUser.objects.filter(email=email).first()
        if temp_user:
            # Check if OTP expired (1 minute)
            if now() - temp_user.created_at < timedelta(minutes=1):
                return Response(
                    {"status": "error", "message": "OTP already sent. Please wait until it expires."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                temp_user.delete()  # Delete expired entry

        # Hash password
        hashed_password = make_password(password)

        # Generate 6-digit OTP
        otp = ''.join(secrets.choice("0123456789") for _ in range(6))

        # Save / update TempUser
        TempUser.objects.update_or_create(
            email=email,
            defaults={
                "username": username,
                "password": hashed_password,
                "otp": otp
            }
        )

        # Send email
        try:
            send_mail(
                "Verify Your Email",
                f"Hello {username},\n\nYour OTP is {otp}",
                "yourgmail@gmail.com",  # replace with your email
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "status": "success",
                "message": f"OTP sent to {email}.",
                "email": email
            },
            status=status.HTTP_200_OK
        )


# from datetime import timedelta
# from django.utils.timezone import now
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import TempUser, AuthUser  # adjust import as needed

class VerifyOTPView(APIView):
    permission_classes = []  # Allow anyone

    def post(self, request):
        email = request.data.get("email")
        entered_otp = request.data.get("otp")

        if not email or not entered_otp:
            return Response(
                {"status": "error", "message": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            temp_user = TempUser.objects.get(email=email)
        except TempUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "No pending signup for this email."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check OTP expiration (1 minute)
        if now() - temp_user.created_at > timedelta(minutes=1):
            temp_user.delete()
            return Response(
                {"status": "error", "message": "OTP expired. Please sign up again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if temp_user.otp == entered_otp:
            # Move to AuthUser
            auth_user = AuthUser.objects.create(
                email=temp_user.email,
                username=temp_user.username,
                password=temp_user.password  # already hashed
            )
            temp_user.delete()
            
            return Response({
                "status": "success",
                "message": "Email verified, account created!",
                "user_id": auth_user.id  # return the newly created user ID
            })

        return Response(
            {"status": "error", "message": "Invalid OTP."},
            status=status.HTTP_400_BAD_REQUEST
        )

    

class UserProfileView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.all()

    def get_object(self):
        user_id = self.kwargs["user_id"]
        return UserProfile.objects.get(user__id=user_id)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs["user_id"]
        try:
            user = AuthUser.objects.get(id=user_id)
        except AuthUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["user"] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)