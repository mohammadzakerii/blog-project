from . import views
from django.urls import path,include

urlpatterns=[
    path("register/",views.register, name="register"),
    path("list/", views.users_list, name="user_list"),
    path("detail/<int:pk>/", views.user_detail, name="user_detail"),
    path("login_user/", views.login_user, name="login_user"),
    path("register/login/otp/", views.RegisterLoginOtp.as_view(), name="register_login_otp"),
    path("check/otp/", views.CheckOtp.as_view(), name="check_otp"),
    path("refresh_access_token/", views.refresh_access_token, name="refresh_access_token"),
    path("logout_user/",views.logout_user, name="logout_user")
]