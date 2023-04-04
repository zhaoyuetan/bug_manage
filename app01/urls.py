from django.urls import path
from app01.views import account

urlpatterns = [

    #腾讯组件，发送短信
    path("send/sms/", account.send_sms,name='send_sms'),#  短信验证码发送
    path("register/", account.register,name='register'),#  注册功能

    
]