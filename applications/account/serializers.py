from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .tasks import send_confirmation_email_celery, send_confirmation_code_celery

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm']

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.pop('password_confirm')
        
        if password1 != password2:
            raise serializers.ValidationError('Passwords are not similar!')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        code = user.activation_code
        send_confirmation_email_celery.delay(user.email, code)
        user.is_active = True
        return user

    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email not registred')
        return email

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email,
                            password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        attrs['user'] = user
        return attrs
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True )
    new_password = serializers.CharField(required = True, min_length = 6)
    new_password_confirm = serializers.CharField(required = True, min_length = 6)
    
    def validate(self, attrs):
        password1 = attrs.get('new_password')
        password2 = attrs.get('new_password_confirm')
        if password1 != password2:
            raise serializers.ValidationError('Passwords are not similar')        
        return attrs

    def validate_old_password(self, password):
        request = self.context.get('request')
        user = request.user
        
        if not user.check_password(password):
            raise serializers.ValidationError('Password is wrong')
        return password
    
    def set_new_password(self):
        user = self.context.get('request').user
        password = self.validated_data.get('new_password')
        user.set_password(password)
        user.save()
        
        
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    
    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('No such user with this email')
        return email
    
    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_confirm_code()
        user.save()
        send_confirmation_code_celery.delay(email, user.confirm_code)
        
        
class ForgotPasswordCompleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirm_code = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length = 6)
    password_confirm = serializers.CharField(required=True, min_length = 6)
    
    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('No such user')
        return email
    
    def validate_code(self, code):
        if not User.objects.filter(confirm_code=code).exists():
            raise serializers.ValidationError('Wrong code')
        return code
    
    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirm')
        
        if password1 != password2:
            raise serializers.ValidationError('Passwords are not similar')
        return attrs
                  
    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.activation_code = ''
        user.save()