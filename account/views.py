from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
  smart_str, 
  force_str, 
  smart_bytes, 
  DjangoUnicodeDecodeError
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .serializers import (
  RegisterSerializer, 
  EmailVerificationSerializer, 
  LoginSerializer, 
  ResetPasswordEmailRequestSerializer,
  SetNewPasswordSerializer,
)
from .models import Account
from .utils import Util
from .renderers import UserRenderer

# Create your views here.
class RegisterView(generics.GenericAPIView):

  serializer_class = RegisterSerializer
  renderer_classes = (UserRenderer,)

  def post(self, request):
    user = request.data
    serializer = self.serializer_class(data = user)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user_data = serializer.data

    user = Account.objects.get(email=user_data['email'])
    token = RefreshToken.for_user(user).access_token

    current_site = get_current_site(request).domain
    relative_link = reverse('verify-email')
    abs_url = f'http://{current_site}{relative_link}?token={token}'

    email_body = f'Hi {user.username} Click on the Link below to verify your email \n {abs_url}'
    data = {
      'email_subject': 'Verify your email',
      'email_body': email_body,
      'to_email': [user.email],
      }
    Util.send_email(data)

    return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
  serializer_class = EmailVerificationSerializer

  token_param_config = openapi.Parameter(
    'token', 
    in_=openapi.IN_QUERY, 
    description='Description', 
    type=openapi.TYPE_STRING
  )

  @swagger_auto_schema(manual_parameters=[token_param_config])
  def get(self, request):
    token = request.GET.get('token')

    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
      user = Account.objects.get(id=payload['user_id'])
      if not user.is_verified:
        user.is_verified = True
        user.save()
      
      return Response({'email': 'Email successfully activated'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError as identifiers:
      return Response({'error': 'Activation Link expired'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError as identifiers:
      return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)



class LoginAPIView(generics.GenericAPIView):
  serializer_class = LoginSerializer

  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
  serializer_class = ResetPasswordEmailRequestSerializer

  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    
    email = request.data['email']
    
    if Account.objects.filter(email=email).exists():
      user = Account.objects.get(email=email)
      uidb64 =urlsafe_base64_encode(smart_bytes(user.id))
      token = PasswordResetTokenGenerator().make_token(user)

      current_site = get_current_site(request).domain
      relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
      abs_url = f'http://{current_site}{relative_link}'

      email_body = f'Hello, \n Use the link below to reset your password \n {abs_url}'
      data = {
        'email_subject': 'Reset Your Password',
        'email_body': email_body,
        'to_email': [user.email],
        }
      Util.send_email(data)

    return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPIView(generics.GenericAPIView):

  def get(self, request, uidb64, token):
    try:
      id = smart_str(urlsafe_base64_decode(uidb64))
      user = Account.objects.get(id=id)

      if not PasswordResetTokenGenerator().check_token(user, token):
              return Response({'error': 'Token is not valid, request a new one'}, status=status.HTTP_401_UNAUTHORIZED)    

      return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
    except DjangoUnicodeDecodeError as identifier:
      return Response({'error': 'Token is not valid, request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):
  serializer_class = SetNewPasswordSerializer

  def patch(self, request):
    serializer = self.serializer_class(data = request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'success': True, 'message': 'Password reset successful'}, status=status.HTTP_200_OK)
