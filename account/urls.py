from django.urls import path
from .views import (
  RegisterView, 
  VerifyEmail, 
  LoginAPIView, 
  PasswordTokenCheckAPIView,
  RequestPasswordResetEmail,
  SetNewPasswordAPIView,
)

urlpatterns = [
  path('register/', RegisterView.as_view(), name='register'),
  path('login/', LoginAPIView.as_view(), name='login'),
  path('email-verfify/', VerifyEmail.as_view(), name='verify-email'),
  path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPIView.as_view(), name='password-reset-confirm'),
  path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
  path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete')
]