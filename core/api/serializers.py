from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class SimpleUserSerializerWithEmail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserSerializerForLogin(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def validate_username(self, username):
        username = username.lower()
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "User doesn't exist.",
            )
        return username


class UserSerializerForSignup(serializers.ModelSerializer):
    username = serializers.CharField(min_length=6, max_length=20)
    password = serializers.CharField(min_length=6, max_length=20)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def validate(self, data):
        username = data['username'].lower()
        email = data['email'].lower()
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                "username": "This username has been occupied",
            })
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "This email has been occupied",
            })
        data['username'] = username
        data['email'] = email
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
