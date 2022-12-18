from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework import status

from django.contrib.auth import get_user_model
from applications.account.serializers import (
    RegisterSerializer,
    LoginSerializer, 
    ChangePasswordSerializer, 
    ForgotPasswordSerializer, 
    ForgotPasswordCompleteSerializer,
)
from rest_framework.response import Response

User = get_user_model()


class RegisterApiView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response('You have been saved well. We have sent you activation code', status=201)


class LoginApiView(ObtainAuthToken):
    serializer_class = LoginSerializer
    

class Change_passwordApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request':request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response('Password changed successfully')  


class ActivationApiView(APIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return Response({'message': 'success'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'wrong code'}, status=status.HTTP_400_BAD_REQUEST)
        

class ForgotPasswordApiView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_code()
        return Response('We have sent you code to recover password')
            
            
class ForgotPasswordCompleteApiview(APIView):
    def post(self, request):
        serializer = ForgotPasswordCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.set_new_password()
        return Response('Your Password is updated successfully')