"""
编写中间件，首先执行谁，要在settings.py的MIDDLEWARE列表设置
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app01.middleware.auth.AuthMiddleware",
]
"""
from django.shortcuts import redirect
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin#导入中间件的类
class AuthMiddleware(MiddlewareMixin):
    """中间件AuthMiddleware"""
    #如果方法没有返回值（返回None），继续向后走
    #如果有返回值，应该和视图函数的返回值类似
    #支持 HttpResponse， render和 redirect
    def process_request(self,request:"HttpRequest"):
        #0. 排除登录页面
        #  判定当前用户请求的url是否为/login/或者图片验证码
        if request.path_info in ["/login/","/image/code/",
                                 "/login/sms/","/send/sms/",
                                 "/index/","/register/"]:
            return None
        #1. 读取用户的session信息，如果可以读取到说明已登录
        user_info_dict = request.session.get("user_info")
        if  user_info_dict:
            return None
        return redirect("/index/")
