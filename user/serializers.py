from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


# CREATE USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "name", "password", "password2")
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6, "required": True},
            "password2": {"write_only": True, "min_length": 6, "required": True},
        }

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})

        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        user = get_user_model().objects.create_user(**validated_data)
        return user


# UPDATE USER SERIALIZER
class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    password2 = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "name", "password", "password2")
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
            "name": {"required": False},
            "password": {"write_only": True, "min_length": 6, "required": False},
            "password2": {"write_only": True, "min_length": 6, "required": False},
        }

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")

        if password or password2:
            if password != password2:
                raise serializers.ValidationError({"password": "Passwords must match."})

        return data

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("password2", None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


# LOGIN/GET TOKEN SERIALIZER
class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if not user:
            msg = "Unable to authenticate with provided credentials"
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
