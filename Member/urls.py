from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import UserProfileView ,UserSignupView



urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path("users/<int:user_id>/profile/", UserProfileView.as_view(), name="user-profile"),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)