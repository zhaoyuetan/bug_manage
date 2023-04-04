from django.db import models

class UserInfo(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=32)
    #  EmailField和CharField区别不在数据库存储，而是在页面展示不同
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=32)
