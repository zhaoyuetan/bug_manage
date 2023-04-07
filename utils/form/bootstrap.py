"""
以后想要使用BootStrapModelForm类，需要做以下这些事情。

# 0.导入所有要用的模块
from django.core.validators import RegexValidator#导入正则表达式校验功能
from django.core.exceptions import ValidationError#导入钩子方法功能

# 1.导入自定义BootStrapModelForm类
from app01.utils.bootsrapmodelform import BootStrapModelForm

# 2.创建一个类继承BootStrapModelForm类
# 3.除了无须init之外和modelform的用法一样
class PrettyModelForm(BootStrapModelForm):
    #校验方式一：正则表达式
    #RegexValidator用正则表达式来校验手机号
    #^正则表达式开头，$正则表达式结尾
    #1[3-9]\d{9}代表第一个数字是1，第二个数字要是3到9，然后是九个整型数字
    #第二个参数是报错反馈信息'手机号格式错误'
    mobile = forms.CharField(
            label="手机号",
            validators=[RegexValidator(r'^1[3-9]\d{9}$','手机号格式错误'),],
    )
    class Meta:
        model = models.PrettyNum
        #exclude=['level']排除字段不展示
        #fields = ['mobile','price','status']
        fields = "__all__"#需要展示全部字段
    #校验方式二：钩子方法
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        if models.PrettyNum.objects.filter(mobile=txt_mobile).exists():
            raise ValidationError("手机号已存在")
        return txt_mobile

# 4.BootStrapForm类同样的，只不过用到Form组件。
"""
from django import forms


class BootStarp:
    bootstrap_exclude_fields = []#不想要该样式的输入框
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 执行父类的init函数
        for name, field in self.fields.items():  # 循环字段名称以及字段对象
            if name in self.bootstrap_exclude_fields:
                continue
            if field.widget.attrs:
                # 如果原来其中有属性，那么为其增加两条
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs['placeholder'] = "请输入" + field.label
            else:
                # 如果原来没有属性，那么为其新建一个attrs参数
                field.widget.attrs = {
                    "class": "form-control",
                    
                    "placeholder": "请输入" + field.label,
                }


# 定义modelform子类，继承modelform类和 BootStarp类
# 命名为 BootStrapModelForm对象
# 继承了modelform的功能，并且增加了创建bootstrap样式的功能
class BootStrapModelForm(BootStarp, forms.ModelForm):
    pass

#与上面同样的，只是运用Form组件
class BootStrapForm(BootStarp, forms.Form):
    pass