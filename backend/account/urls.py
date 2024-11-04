from django.urls import path
from .apis import UserRegisterApi,UserLoginApi
from .apis import modifyPasswordApi,modifyEmailApi,modifyPhoneApi,modifyGenderApi,modifyNameApi
from .apis import Is_PasswordApi,ResetPasswordApi,checkphoneApi,GetAllUserInfoApi,askUserlengthApi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="register"),
    path("login/", UserLoginApi.as_view(), name="Login"),
    path("token_obtain/", TokenObtainPairView.as_view(), name="obtain"),
    path("token_refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("token_verify/", TokenVerifyView.as_view(), name="verify"),
    path("isPassword/",Is_PasswordApi.as_view(),name="isPassword"),
    path("resetPassword/",ResetPasswordApi.as_view(),name="resetPassword"),
    path("modify/password/",modifyPasswordApi.as_view(),name="modifyPassword"),
    path("modify/email/",modifyEmailApi.as_view(),name="modifyEmail"),
    path("modify/phone_number/",modifyPhoneApi.as_view(),name="modifyPhone"),
    path("modify/gender/",modifyGenderApi.as_view(),name="modifyGender"),
    path("modify/name/",modifyNameApi.as_view(),name="modifyName"),
    path("checkphone/",checkphoneApi.as_view(),name="checkphone"),
    path("getAllUserInfo/",GetAllUserInfoApi.as_view(),name="getAllUserInfo"),
    path("getUserLength/",askUserlengthApi.as_view(),name="getUserLength"),
]
