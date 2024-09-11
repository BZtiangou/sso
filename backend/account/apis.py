from .models import CustomUser
from .serializers import modifyPhoneSerializer,modifyEmailSerializer,modifyPasswordSerializer,UserLoginSerializer,UserSerializer,IsPasswordSerializer,ResetSerializer,modifyNameSerializer
from .serializers import modifyGenderSerializer,userInfoSerializer,CheckPhoneSerializer,CustomTokenObtainPairSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils import timezone
from base import email_inf
from django.utils.timezone import now
from datetime import timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from django_otp.decorators import otp_required
from Crypto.Cipher import AES
import base64
import dotenv  
import os 
from pathlib import Path
import ast  # 用来将字符串解析为字节串
import codecs  # 用于处理转义字符的字符串
# 加密
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(dotenv_path=BASE_DIR / ".env", verbose=True)
key =  os.environ.get(
    'PYOTP_SECRET_KEY',
    '8\xae\xdbp|h\x80\n\xfd\x9f\xa1\xfb\xf6W$\xd6'
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class getUserInfoApi(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = []
    # @otp_required  # 添加此装饰器以要求TOTP验证
    def post(self, request):
        serializer = userInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_user_model().objects.get(name=serializer.validated_data["name"])
        except ObjectDoesNotExist:
            return Response({"message": "User not registered"}, status=status.HTTP_400_BAD_REQUEST)
        key_bytes = b'\x10R\\\x08\xaa3E\xef\x1b\x85z,R\xa2\xe25'
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        plaintext = b'6666666666666666'
        enc = cipher.encrypt(plaintext)
        # print(base64.b64encode(enc).decode('utf-8'))  # 打印加密后的结果
        # 将加密后的数据编码为base64
        enc_base64 = base64.b64encode(enc).decode('utf-8')
        # 解密
        decipher = AES.new(key_bytes, AES.MODE_ECB)
        dec = decipher.decrypt(enc)
        if enc_base64 == serializer.validated_data["otp"]:
            return Response(user.username)
        else:
            return Response({"message": "OTP verification failed"}, status=status.HTTP_401_UNAUTHORIZED)
        
    
#注册api
class UserRegisterApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registration succeeded"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 存入cookie版本
class UserLoginApi(APIView):
    permission_classes = []

    def post(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_user_model().objects.get(username=serializer.validated_data["username"])
        except ObjectDoesNotExist:
            return Response({"message": "User not registered"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(serializer.validated_data["password"]):
            refresh = RefreshToken.for_user(user)
            
            # 使用自定义的TokenObtainPairSerializer生成token
            custom_token_serializer = CustomTokenObtainPairSerializer()
            token = custom_token_serializer.get_token(user)
            # 根据邮箱是否为空设置status的值
            if not user.email :
                response = Response({
                    "username": user.username,
                    "refresh": str(refresh),
                    "access": str(token.access_token),
                    "expire": token.access_token.payload["exp"] - token.access_token.payload["iat"],
                },status=520)

                # 设置访问令牌的Cookie
                max_age = 60 * 60 * 24 * 1   # 设置Cookie有效期为1天
                expires = now() + timedelta(seconds=max_age)
                response.set_cookie(
                    'jwt_token',  # Cookie的名称
                    str(token.access_token),  # Cookie的值，这里是访问令牌
                    max_age=max_age,  # Cookie的有效期
                    httponly=False,  
                    domain='abdn.kirisame.cc',  # 设置cookie的域名
                    # domain='127.0.0.1',
                    # secure=True,  # 如果使用HTTPS，则设置为True
                )

                return response
            else:
                response = Response({
                    "username": user.username,
                    "refresh": str(refresh),
                    "access": str(token.access_token),
                    "expire": token.access_token.payload["exp"] - token.access_token.payload["iat"],
                })
                # 设置访问令牌的Cookie
                max_age = 60 * 60 * 24 * 1   # 设置Cookie有效期为1天
                expires = now() + timedelta(seconds=max_age)
                response.set_cookie(
                    'jwt_token',  # Cookie的名称
                    str(token.access_token),  # Cookie的值，这里是访问令牌
                    max_age=max_age,  # Cookie的有效期
                    httponly=False,  
                    domain='abdn.kirisame.cc',  # 设置cookie的域名
                    # domain='127.0.0.1',
                    # secure=True,  # 如果使用HTTPS，则设置为True
                )
                return response
        else:
            return Response({"message": "User login failed, please check your account password"}, status=status.HTTP_401_UNAUTHORIZED)


# 检查手机号码是否正确
class checkphoneApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = CheckPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        username = request.user.username

        try:
            user = get_user_model().objects.get(phone_number=phone_number, username=username)
            return Response("Accept", status=status.HTTP_200_OK)
        except get_user_model().DoesNotExist:
            return Response("手机号码不存在", status=status.HTTP_400_BAD_REQUEST)



# 令牌发送api 通用api
class Is_PasswordApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = IsPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.get(username=serializer.validated_data["username"]) == None:
            return Response("用户不存在",status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.get(username=serializer.validated_data["username"])
        if user.email == serializer.validated_data["email"]:
            token_value = get_random_string(length=6)
            user.token = token_value
            user.token_expires = timezone.now() + timezone.timedelta(minutes=2)  # 设置2分钟后过期
            user.save()
            send_mail(
                '重置密码',
                message=f'您正在尝试找回密码或者修改其他验证信息，您的令牌是{token_value}',
                from_email=email_inf.EMAIL_FROM,
                recipient_list=[user.email],
            )
            return Response({
                "Token email has been sent to your reserved mailbox, please check!"
            })
        else:
            return Response("The mailbox is incorrect or does not exist",status=status.HTTP_400_BAD_REQUEST)


# 后续感觉需要添加验证码等防爆破
class ResetPasswordApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            if serializer.validated_data['token'] == user.token and user.token_expires and timezone.now() <= user.token_expires:
                user = get_user_model().objects.get(username=serializer.validated_data['username'])
                # 更新密码前，先使用 set_password 方法加密密码
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({
                    f"Your password has been changed successfully. Please log in again"
                })
            else:
                return Response({
                    "令牌超时或错误"
                })
        else :
            return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

# 普通修改密码
class modifyPasswordApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = modifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取用户
        username = request.user.username
        user = get_user_model().objects.get(username=username)
        
        # 检查新密码长度
        new_password = serializer.validated_data['password']
        if len(new_password) < 6:
            return Response({"error": "The new password must be longer than 6 characters."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 验证旧密码
        if user.check_password(serializer.validated_data['old_password']):
            # 设置新密码
            user.set_password(new_password)
            user.save()
            return Response({"message": "Your password has been changed successfully. Please log in again."})
        
        # 如果旧密码不匹配或用户不存在
        return Response({"error": "The old password is incorrect or the user does not exist."},
                        status=status.HTTP_400_BAD_REQUEST)
# class modifyPhoneApi(APIView):
#     permission_classes = []
#     def post(self, request: Request) -> Response:
#         serializer = modifyPhoneSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         if get_user_model().objects.get(username=username):
#             user = get_user_model().objects.get(username=username)
#             if serializer.validated_data['token'] == user.token and timezone.now() <= user.token_expires:
#                 user = get_user_model().objects.get(username=serializer.validated_data['username'])
#                 user.phone_number = serializer.validated_data['phone_number']
#                 user.save()
#                 return Response({
#                     f"您的手机号修改成功!"
#                 })
#             else:
#                 return Response({
#                     "令牌超时或错误"
#                 })
#         else :
#             return Response({"The user name does not exist"},status=status.HTTP_404_NOT_FOUND)

# class modifyEmailApi(APIView):
#     permission_classes = []
#     def post(self, request: Request) -> Response:
#         serializer = modifyEmailSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         if get_user_model().objects.get(username=username):
#             user = get_user_model().objects.get(username=username)
#             if serializer.validated_data['token'] == user.token and timezone.now() <= user.token_expires:
#                 user = get_user_model().objects.get(username=serializer.validated_data['username'])
#                 user.email = serializer.validated_data['email']
#                 user.save()
#                 return Response({
#                     f"Your email address has been successfully modified!"
#                 })
#             else:
#                 return Response({
#                     "令牌超时或错误"
#                 })
#         else :
#             return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

# 无安全验证版本
class modifyEmailApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.email= serializer.validated_data['email']
            user.save()
            return Response("email modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

class modifyPhoneApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.phone_number= serializer.validated_data['phone_number']
            user.save()
            return Response("phone modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

        
class modifyGenderApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyGenderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.gender= serializer.validated_data['gender']
            user.save()
            return Response("Gender modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

class modifyNameApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.name= serializer.validated_data['name']
            user.save()
            return Response("Name changed successfully")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)