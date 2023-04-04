import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from django_redis import get_redis_connection

from app01 import models
from utils.tencent.sms import send_sms_single  # 导入发送单条短信


class SendSmsForm(forms.Form):
    #  正则表示式方法校验手机号格式是否正确
    mobile_phone = forms.CharField(label="手机号", validators=[
                                   RegexValidator(r'^(1[3-9])\d{9}$', '手机号格式不正确'),])
    #  通过重写初始化函数，可以将视图函数的值传递来
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """
        钩子法校验手机号是否存在和tql参数:
        手机号校验：
            手机号的格式已经在正则表达式校验中完成
            此处我们用来判断数据库该手机号是否存在，不允许重复注册
        获取到request的GET请求传输的tpl数据
            ?tpl = login ->登录的模板ID
            ?tpl = register ->注册的模板ID
            settings.TENCENT_SMS_TEMPLATE是一个字典，键是login和register，值是模板ID
            tpl如果取login和register时候可以在字典TENCENT_SMS_TEMPLATE中取值
            否则说明短信模板错误，在此处给予校验
        """
        #  获取到用户输入的手机号
        mobile_phone = self.cleaned_data['mobile_phone']

        #  检验tpl格式是否正确
        #  把tpl参数获取到
        tpl = self.request.GET.get('tpl')
        #  获取到TENCENT_SMS_TEMPLATE字典中以 tpl为键的值
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        #  如果字典中没有这个值，template_id为空
        if not template_id:
            raise ValidationError('短信模板错误')

        #  检验数据库是否已经有此手机号
        exists = models.UserInfo.objects.filter(
            mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已存在')
        """
        #  发短信给用户
        #  随机四位数验证码
        code = random.randrange(1000, 9999)
        #  给用户发短信，参数依次为：手机号，短信模板ID和字符串格式化参数列表
        res = send_sms_single(mobile_phone, template_id, [code, 1])
        #  判断短信发送是否成功
        if res["result"] != 0:
            #  当res["result"] != 0，表示发送短信错误
            raise ValidationError("短信发送失败，{}".format(res["errmsg"]))

        #  验证码写入redis（使用django_redis模块）
        #  连接名为 "default" 的redis
        conn = get_redis_connection("default")
        #  键是mobile_phone，值是code验证码，有效时间是60秒
        conn.set(mobile_phone,code,ex=60)
        #  获取存储的键为mobile_phone的值，60秒内有效
        value = conn.get(mobile_phone)
        print(value)
        """

        return mobile_phone


class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(label="手机号", validators=[
                                   RegexValidator(r'^(1[3-9])\d{9}$', '手机号格式不正确'),])
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="重复密码")
    code = forms.CharField(label="验证码")

    class Meta:
        model = models.UserInfo
        fields = ["username", "email", "password",
                  "confirm_password", "mobile_phone", "code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = "请输入" + field.label
