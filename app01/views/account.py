from io import BytesIO

from django.http import HttpRequest,JsonResponse
from django.shortcuts import HttpResponse,render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from django_redis import get_redis_connection

from app01 import models
from utils.account.encrypt import md5
from utils.account.code import check_code
from app01.forms.account import RegisterModelForm,SendSmsForm,LoginSmsForm,LoginForm

def logout(request:"HttpRequest"):
    #  清空session缓存，使得登录状态取消
    request.session.flush()
    #  直接用url的别名访问网页
    return redirect('index')

def image_code(request:"HttpRequest"):
    """ 生成图片验证码 """
    #  生成图片验证码
    img,code_string = check_code()
    #  把验证码答案写道session中，以便于后续获取
    request.session["image_code"] = code_string
    #  设置六十秒之后超时，60秒后验证码无效
    request.session.set_expiry(60)
    #  写入内存(BytesIO)
    stream = BytesIO()
    img.save(stream, 'png')#  用png格式把图片写到内存
    return HttpResponse(stream.getvalue())#  把图片给用户返回

def login(request: "HttpRequest"):
    """ 短信登录功能 """
    if request.method == "GET":      
        form = LoginForm(request=request)
        return render(request,"login.html",{"form":form})
    form = LoginForm(request=request,data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        #  由于我们想让用户可以使用邮箱或者手机号来登录
        #  因此，我们用 Q来构造复杂的搜索
        #  Q()|Q()是或，再来一个filter是且
        user_object = models.UserInfo.objects.filter(
            Q(email=username)|Q(mobile_phone=username)
            ).filter(password=password).first()
        if user_object:
            #  用户名和密码匹配，用户登录成功
            #  清空session缓存，使得验证码失效
            request.session.clear()  # 登录成功后把验证码删掉
            #  登录成功后，把用户信息放入session，保持登录状态
            request.session["user_info"] = {
                'user_id':user_object.id,
                'user_name':user_object.username
            }
            #  两周内免密登录
            request.session.set_expiry(60 * 60 *24 * 14)
            return redirect("/index/")
        form.add_error('username','用户名或密码错误')
    #  用户登录失败给出错误提示，此时form的errors包含错误信息
    return render(request,"login.html",{"form":form})

@csrf_exempt#在这个函数开头写这个。免除post请求的crsftoken验证
def login_sms(request: "HttpRequest"):
    """ 短信登录功能 """
    if request.method == "GET":      
        form = LoginSmsForm()
        return render(request,"login_sms.html",{"form":form})
    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        #  用户登录成功
        #  我们在钩子方法中直接把用户对象赋值给了mobile_phone字段
        #  登录成功后，把用户信息放入session，保持登录状态
        user_object = form.cleaned_data['mobile_phone']
        #  登录成功要删除redis中的验证码
        conn = get_redis_connection("default")
        conn.delete(user_object.mobile_phone)
        #  登录成功后，把用户信息放入session，保持登录状态
        request.session["user_info"] = {
            'user_id':user_object.id,
            'user_name':user_object.username
        }
        #  两周内免密登录
        request.session.set_expiry(60 * 60 *24 * 14)
        return JsonResponse({"status":True,"data":"/index/"})
    #  用户登录失败给出错误提示
    return JsonResponse({"status":False,"error":form.errors})

def register(request: "HttpRequest"):
    """短信验证码发送"""
    if request.method == "GET":
        #  验证通过后写入数据库
        form = RegisterModelForm()
        return render(request, "register.html",{"form":form})
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        #  可以在此处进行密码的MD5加密
        #  form.instance.password = md5(form.instance.password)       
        #  注册成功要删除redis中的验证码
        conn = get_redis_connection("default")
        conn.delete(request.POST.get('mobile_phone'))
        form.save() #  把数据库中有的字段保存
        #  如果校验正确，给ajax请求返回状态为True
        return JsonResponse({"status":True,'data':'/login/'})
    #  如果校验失败给ajax返回专题为False，并且把错误信息列表传递过去
    return JsonResponse({"status":False,"error":form.errors})

def send_sms(request: "HttpRequest"):
    """短信验证码发送"""
    #  把request传到form组件，在form组件完成以下操作：
    #  校验手机号和tpl参数格式
    #  校验成功发送短信并报存到redis中
    form = SendSmsForm(request=request,data=request.GET)
    if form.is_valid():
        #  如果校验正确，给ajax请求返回状态为True
        return JsonResponse({"status":True})
    #  如果校验失败给ajax返回专题为False，并且把错误信息列表传递过去
    return JsonResponse({"status":False,"error":form.errors})


