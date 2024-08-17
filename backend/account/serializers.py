from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:  
        model = CustomUser
        fields = [
            "username",
            "password",
            "email",
            "device",
            "phone_number",
            "name",
        ]
    email = serializers.EmailField(
        required=True
    )
    name = serializers.CharField(
        max_length=20,
        required=True
    )
    def create(self, validated_data: dict) -> CustomUser:
        #密码单独拿出来，因为需要加密后才能存在数据库
        password = validated_data.pop("password")
        #创建实例user
        user = get_user_model().objects.create_user(**validated_data)
        #加密
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=150,
        required=True
    )
    password = serializers.CharField(
        max_length=128,
        required=True
    )

# 通用验阵
class IsPasswordSerializer(serializers.Serializer):
    email=serializers.CharField(
       required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True
    )

class ResetSerializer(serializers.Serializer):
    token=serializers.CharField(
        required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    password= serializers.CharField(
        max_length=128,
        required=True
    )

class modifyPasswordSerializer(serializers.Serializer):
    password= serializers.CharField(
        max_length=128,
        required=True
    )

    old_password= serializers.CharField(
        max_length=128,
        required=True
    )


# 手机号修改
class modifyPhoneSerializer(serializers.Serializer):
    # username = serializers.CharField(
    #     max_length=150,
    #     required=True
    # )
    
    phone_number= serializers.CharField(
        max_length=11,
        required=True
    )
    # token=serializers.CharField(
    #     required=True
    # )

# 邮箱修改
class modifyEmailSerializer(serializers.Serializer):
    # username = serializers.CharField(
    #     max_length=150,
    #     required=True
    # )
    email= serializers.CharField(
        max_length=150,
        required=True
    )
    # token=serializers.CharField(
    #     required=True
    # )

class modifyGenderSerializer(serializers.Serializer):
    gender= serializers.CharField(
        max_length=10,
        required=True
    )

class modifyNameSerializer(serializers.Serializer):
    name= serializers.CharField(
        max_length=20,
        required=True
    )

class userInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "phone_number",
            "name",
            "gender",
        ]
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['username'] = user.name
#         return token

class CheckPhoneSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        fields = [
            'phone_number',
        ]
    phone_number= serializers.CharField(
        max_length=11,
        required=True
    )