"""
使用离线脚本插入数据
"""
import os
import sys
import django
#  python导包的时候会在sys.path的路径中依次寻找模块位置
#  想要导入models模块，必须让项目根目录即app01的父亲目录在sys.path中
#  此时，执行这个离线脚本是在scripts目录执行，scripts目录会被添加到sys.path
#  但是，django的根目录也就是scripts的父亲目录，并没有被导入到sys.path，自然无法导入models模块
#  因此，我们需要手动把django的根目录添加到sys.path
#  os.path.abspath(__file__)，这个是当前运行的脚本的绝对路径
#  os.path.dirname（）当前文件所在的文件夹，也就是scripts
#  再找一次就是scripts所在的文件夹，也就是django项目的根目录
#  执行离线脚本的时候会在scripts目录执行，会自动将scripts目录添加到sys.path
#  django.setup()内部读取os.environ['DJANGO_SETTINGS_MOUDLE']
#  可以通过django.setup()，让django模拟启动，但是他不知道连接哪个django
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)#  把django项目的根目录添加到sys.path
os.environ.setdefault("DJANGO_SETTINGS_MODULE","bug_manage_code.settings")
django.setup()


#  上面的工作都做完了，才能导入models模块并成功执行
from app01 import models
#  默认情况下离线脚本不能调用，运行时的django程序
models.UserInfo.objects.create(username='陈硕',
                               email="chenshuo@live.com",
                               mobile_phone='13838380000',
                               password='12312354648'
                            )



