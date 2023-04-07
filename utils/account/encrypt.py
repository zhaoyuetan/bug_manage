import hashlib
from django.conf import settings
#  对密码进行md5加密保存
def md5(password):
    #  django自带生成的随机字符串作为盐
    salt = settings.SECRET_KEY
    obj = hashlib.md5(salt.encode('utf-8'))
    obj.update(password.encode('utf-8'))
    return obj.hexdigest() 
