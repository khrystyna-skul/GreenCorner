from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True) 
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True) 
    email = serializers.EmailField(required=True) 
    password = serializers.CharField(write_only=True, required=True, min_length=8) 
    password_confirm = serializers.CharField(write_only=True, required=True) 

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_confirm') 

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Користувач із таким email вже існує.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Паролі не збігаються."}) 
        
        user = User(username=attrs.get('username'), email=attrs.get('email'))
        validate_password(attrs['password'], user=user)
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(**validated_data)
        return user