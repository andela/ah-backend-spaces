from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    GoogleSocialAuthAPIView, FacebookSocialAuthAPIView, VerifyAPIView,
    ResetPasswordAPIView, UpdatePasswordAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('auth/google/', GoogleSocialAuthAPIView.as_view()),
    path('auth/facebook/', FacebookSocialAuthAPIView.as_view()),
    path('activate/<str:token>', VerifyAPIView.as_view()),
    path('user/reset_password/', ResetPasswordAPIView.as_view()),
    path('user/new_password/<str:token>/', UpdatePasswordAPIView.as_view())
]
