from django.http import HttpRequest,JsonResponse
from django.shortcuts import HttpResponse,render

from app01.forms.account import RegisterModelForm,SendSmsForm

def register(request: "HttpRequest"):
    """短信验证码发送"""
    if request.method == "GET":
        form = RegisterModelForm()
        return render(request, "register.html",{"form":form})
    print (request.POST)
    form = RegisterModelForm()
    if form.is_valid():
        #  如果校验正确，给ajax请求返回状态为True
        return JsonResponse({"status":True})
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


