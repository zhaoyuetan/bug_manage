import random

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import HttpResponse

from utils.tencent.sms import send_sms_single  # 导入发送单条短信


def send_sms(request: "HttpRequest"):
    """
    短信验证码发送：
    ?tpl = login ->登录的模板ID
    ?tpl = register ->注册的模板ID
    settings.TENCENT_SMS_TEMPLATE是一个字典，键是login和register，值是模板ID
    """
    #  获取GET请求穿的参数tpl，代表是登录还是注册
    tpl = request.GET.get("tpl")
    #  通过配置文件中将login和register作为key的字典，读取模板ID值
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    #  随机四位数验证码
    code = random.randrange(1000, 9999)
    #  中间的是模板ID，后面的列表是该模板需要的格式化参数
    res = send_sms_single("手机号", template_id, [code, 5])
    if res["result"] == 0:
        return HttpResponse("成功")  # result不为0的时候说明有错
    else:
        #  输出手机号格式错误
        return HttpResponse(res["errmsg"])
