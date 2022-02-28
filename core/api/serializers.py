from rest_framework import serializers

from core.models import User, UserProfile


class SimpleUserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        profile = obj.profile
        if profile.avatar:
            return profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar_url']


class SimpleUserSerializerWithEmail(SimpleUserSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'avatar_url']


class UserSerializer(SimpleUserSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nickname', 'avatar_url',
        ]


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


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    nickname = serializers.CharField(
        min_length=1, max_length=140, required=False
    )
    avatar = serializers.FileField(required=False)

    class Meta:
        model = UserProfile
        fields = ['nickname', 'avatar']
