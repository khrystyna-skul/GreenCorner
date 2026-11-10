from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True) #
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True) #
    email = serializers.EmailField(required=True) #[cite: 4]
    password = serializers.CharField(write_only=True, required=True, min_length=8) #[cite: 4]
    password_confirm = serializers.CharField(write_only=True, required=True) #[cite: 4]

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_confirm') #[cite: 4]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Користувач із таким email вже існує.")
        return value

    def validate(self, attrs):
        # 1. Перевірка збігу паролів[cite: 4]
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Паролі не збігаються."}) #[cite: 4]
        
        # 2. Перевірка складності пароля стандартними засобами Django[cite: 4]
        user = User(username=attrs.get('username'), email=attrs.get('email'))
        validate_password(attrs['password'], user=user)
        
        return attrs

    def create(self, validated_data):
        # Видаляємо password_confirm перед збереженням
        validated_data.pop('password_confirm')
        
        # create_user автоматично ХЕШУЄ пароль[cite: 4]
        user = User.objects.create_user(**validated_data)
        return user