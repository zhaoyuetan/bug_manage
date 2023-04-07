import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from django_redis import get_redis_connection

from app01 import models
from utils.account.encrypt import md5#  md5加密 
from utils.tencent.sms import send_sms_single  # 导入发送单条短信
from utils.form.bootstrap import BootStrapForm,BootStrapModelForm #  导入带有bootstrap样式的表单组件 


class LoginForm(BootStrapForm):
    """
    Form组件：密码登录
    """ 
    username = forms.CharField(label='邮箱或手机号')
    #  render_value = True 让用户即使是输错了密码也不会置空
    password = forms.CharField(label='密码',widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    #  通过重写初始化函数，可以将视图函数的值传递来
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_code(self):
        code = self.cleaned_data['code']#  用户输入的验证码
        session_code = self.request.session.get("image_code")#  获取session的验证码
        if not session_code:
            raise ValidationError("验证码已过期，请重新获取")
        #  不考虑大小写错误和验证码中间用空格
        if code.strip().upper() != session_code.upper():
            raise ValidationError("验证码输入错误")
        return code
    
    def clean_password(self):
        #  把密码加密，然后把密码和用户名的验证放到视图函数
        pwd = self.cleaned_data['password']
        return md5(pwd)

class LoginSmsForm(BootStrapForm):
    """
    Form组件：短信登录
    """ 
    #  正则表示式方法校验手机号格式是否正确
    mobile_phone = forms.CharField(label="手机号", validators=[
                                   RegexValidator(r'^(1[3-9])\d{9}$', '手机号格式不正确'),])
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput()
    )
    def clean_mobile_phone(self):
        """验证手机号是否已经注册"""
        mobile = self.cleaned_data['mobile_phone']
        #  如果手机号已经注册，可以直接根据手机号获取到用户对象
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile).first()
        if not user_object:
            raise ValidationError("手机号未注册，请先注册")
        #  把用户对象直接赋值给mobile_phone字段
        return user_object
    
    def clean_code(self):
        """校验验证码是否正确"""
        code = self.cleaned_data['code']
        #  通过mobile_phone字段获取用户对象
        user_object = self.cleaned_data.get('mobile_phone')
        if not user_object:
            #  用户对象不存在直接返回，因为在上一步已经报错
            return code
        conn = get_redis_connection("default")
        redis_code = conn.get(user_object.mobile_phone)
        if not redis_code:
            raise ValidationError("验证码已失效，请重新获取")
        str_redis_code = redis_code.decode("utf-8")
        if code.strip() != str_redis_code:
            raise ValidationError("验证码错误，请重新输入")
        return code

class SendSmsForm(forms.Form):
    """
    Form组件：用户注册的时候点击获取验证码传入手机号并校验
    """
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
        if tpl == 'register':
            if exists:
                raise ValidationError('手机号已注册')
        else:
            if not exists:
                raise ValidationError('手机号未注册，请先注册')

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
        #  value = conn.get(mobile_phone)
        #  print(value)

        return mobile_phone


class RegisterModelForm(BootStrapModelForm):
    """
    ModelForm组件：用户注册的时候的传入数据校验
    """
    password = forms.CharField(
        label="密码", 
        #  min_lenth规定最小长度，错误提示报错方式可以看error_messages参数。
        min_length=8,
        max_length=64,
        error_messages={
            'min_length':"密码不能小于8个字符",
            'max_length':"密码不能大于64个字符"
        },
        widget=forms.PasswordInput(render_value=True),
    )
    confirm_password = forms.CharField(
        label="重复密码", 
        #  min_lenth规定最小长度，错误提示报错方式可以看error_messages参数。
        min_length=8,
        max_length=64,
        error_messages={
            'min_length':"密码不能小于8个字符",
            'max_length':"密码不能大于64个字符"
        },
        widget=forms.PasswordInput(render_value=True)
    )
    mobile_phone = forms.CharField(
        label="手机号", 
        validators=[
            RegexValidator(r'^(1[3-9])\d{9}$', '手机号格式不正确')
        ]
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput()
    )

    class Meta:
        model = models.UserInfo
        fields = ["username", "email", "password",
                  "confirm_password", "mobile_phone", "code"]
            

    def clean_username (self):
        """校验用户名是否重复"""
        username = self.cleaned_data["username"]
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError("用户名已存在")
        return username
    
    def clean_email(self):
        """邮箱校验是否重复，格式由Emailfield来校验"""
        email = self.cleaned_data["email"]
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError("邮箱已注册")
        return email       
    
    def clean_password(self):
        pwd = self.cleaned_data['password']
        return md5(pwd)

    def clean_confirm_password(self):
        """校验重复密码和第一次密码输入是否一致"""
        #  由于按照fields列表的顺序执行钩子
        #  此处的密码已经进行过 md5 加密，只需要给重复密码进行加密
        pwd = self.cleaned_data.get('password')
        confirm_pwd = md5(self.cleaned_data['confirm_password'])
        if not pwd:
            return confirm_pwd
        if pwd != confirm_pwd:
            raise ValidationError("两次密码不一致")
        return confirm_pwd
    
    def clean_mobile_phone(self):
        """校验手机号是否已经注册"""
        mobile = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile).exists()
        if exists :
            raise ValidationError("手机号已注册")
        return mobile

    def clean_code(self):
        """校验用户验证码输入是否正确，以及是否给该手机发送过验证码"""
        code = self.cleaned_data['code']
        #  中中括号加上key如果key不存在会报错KeyError
        #  mobile = self.cleaned_data['mobile_phone'] 
        #  用get即使是没有mobile_phone这个key会获得none
        mobile = self.cleaned_data.get('mobile_phone')
        if not mobile:
            #  如果mobile没有校验通过我们是取不到mobile的
            #  后续用redis连接可能会报错，没有这样的键
            return code
        #  连接redis获取给用户发送的验证码 
        conn = get_redis_connection("default")
        #  获取存储的键为mobile的值，也就是对应的验证码
        #  如果获取不到redis存储的验证码，报错没有验证码
        redis_code = conn.get(mobile)
        if not redis_code:
            raise ValidationError("验证码失效或未发送，请重新发送")
        #  在redis是以字节的形式存储，因此要用utf-8给解码，decode一下得到验证码
        redis_str_code = redis_code.decode('utf-8')
        print(redis_code)
        #  strip()去掉用户输入的空白，用户输入空格将不影响注册
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误，请重新输入")
        
        return code
        