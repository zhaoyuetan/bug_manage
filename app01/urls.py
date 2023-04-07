from django.urls import path
from app01.views import account,home

urlpatterns = [

    #  主页首页
    path("index/", home.index,name='index'),#  密码登录功能

    #账户注册和登录
    path("send/sms/", account.send_sms,name='send_sms'),#  短信验证码发送
    path("register/", account.register,name='register'),#  注册功能
    path("login/sms/", account.login_sms,name='login_sms'),#  短信登录功能
    path("login/", account.login,name='login'),#  密码登录功能
    path("image/code/", account.image_code,name='image_code'),#  密码登录功能
    path("logout/", account.logout,name='logout'),#  退出登录功能
    
]