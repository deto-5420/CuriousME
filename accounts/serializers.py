from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,Http404
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.hashers import check_password

from .tokens import account_activation_token
from .models import User, Profile


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':'password'}, min_length=8, max_length=16, write_only=True)
    password2 = serializers.CharField(style={'input_type':'password'}, min_length=8, max_length=16, write_only=True)

    class Meta:
        model = User
        fields = ['email','username','password','password2']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def save(self):    
        user = User(
                email=self.validated_data['email'],
                username= self.validated_data['username'],
        )

        password=self.validated_data['password']
        password2=self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password':'Passwords must match'})

        user.set_password(password)
        user.is_active = False
        user.save()
        user.refresh_from_db()

        return user

class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=4)

    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type':'password'}, min_length=8, max_length=16, write_only=True)
    confirm_password = serializers.CharField(style={'input_type':'password'}, min_length=8, max_length=16, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    
    class Meta:
        fields = ['new_password', 'confirm_password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')

            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if new_password != confirm_password:
                raise AuthenticationFailed("Passwords Doesn't match.", 401) 

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Reset link is valid', 401)

            user.set_password(new_password)
            user.save()
            return user

        except Exception as e:
            raise AuthenticationFailed(e, 401)

        return super().validate(attrs)

