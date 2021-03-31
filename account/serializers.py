from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
  smart_str, 
  force_str, 
  smart_bytes, 
  DjangoUnicodeDecodeError
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from .models import Account
from .utils import Util

class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(max_length=80, min_length=6, write_only=True)

  class Meta:
    model = Account
    fields = ['email', 'username', 'password']

  def validate(self, attrs):
    email = attrs.get('email', '')
    username = attrs.get('username', '')

    if not username.isalnum():
      raise serializers.ValidationError('The username should only contain alphanumeric characters')

    return attrs

  def create(self, validated_data):
    return Account.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
  token = serializers.CharField(max_length=600)

  class Meta:
    model = Account
    fields = ['token']

class LoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  password = serializers.CharField(max_length=80, min_length=6, write_only=True)
  username = serializers.CharField(max_length=70, read_only=True)
  tokens = serializers.CharField(max_length=70, read_only=True)


  class Meta:
    model = Account
    fields = ['email', 'password', 'username', 'tokens']

  def validate(self, attrs):
    email = attrs.get('email', '')
    password = attrs.get('password', '')

    user = auth.authenticate(email=email, password=password)

    if not user:
      raise AuthenticationFailed('Invalid credentials, try again')
    if not user.is_active:
      raise AuthenticationFailed('Account disabled, contact admin')
    if not user.is_verified:
      raise AuthenticationFailed('Email is not verified')
    

    return {
      'email': user.email,
      'username': user.username,
      'tokens': user.tokens(),
    }

    return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
  email = serializers.EmailField(min_length=2)

  class Meta:
    fields = ['email',]
        

class SetNewPasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=60, min_length=6, write_only=True)
  token = serializers.CharField(max_length=60, min_length=1, write_only=True)
  uidb64 = serializers.CharField(max_length=60, min_length=1, write_only=True)

  class Meta:
    fields = ['password', 'token', 'uidb64']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      token = attrs.get('token')
      uidb64 = attrs.get('uidb64')

      id = force_str(urlsafe_base64_decode(uidb64))
      user = Account.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise AuthenticationFailed('The reset link is invalid', 401)

      user.set_password(password)
      user.save()
      return user
    except Exception as e:
      raise AuthenticationFailed('The reset link is invalid', 401)

    return super().validate(attrs)




