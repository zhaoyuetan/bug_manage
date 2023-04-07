from django.db import models

class UserInfo(models.Model):
    #  如果想要让之后查询更快，可以用 db_index为 True，这样数据库会给他自动生成索引
    username = models.CharField(verbose_name="用户名", max_length=32)
    #  EmailField和CharField区别不在数据库存储，而是在页面展示不同
    #  EmailField自带了校验格式功能
    email = models.EmailField(verbose_name="邮箱", max_length=32,db_index=True)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32,db_index=True)
    password = models.CharField(verbose_name="密码", max_length=32,db_index=True)
