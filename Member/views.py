from rest_framework import generics, permissions
from .models import AuthUser, UserProfile
from .serializers import AuthUserSerializer, UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status


# --- User Signup View ---
class UserSignupView(generics.CreateAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    permission_classes = [permissions.AllowAny] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            status=status.HTTP_201_CREATED
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