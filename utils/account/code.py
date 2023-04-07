"""
验证码生成组件，以后想要使用需要做这几件事情：

# 0.把相关字体存放在项目根目录，和manage.py在同一个文件夹

#视图函数中
# 1. 将生成的图片读取
from io import BytesIO
def image_code(request:"HttpRequest"):
    #生成图片验证码
    img,code_string = check_code()
    #把验证码答案写道session中，以便于后续获取
    request.session["image_code"] = code_string
    #设置六十秒之后超时，60秒后验证码无效
    request.session.set_expiry(60)
    #写入内存(BytesIO)
    stream = BytesIO()
    img.save(stream, 'png')#用png格式把图片写到内存
    return HttpResponse(stream.getvalue())#把图片给用户返回

# 2.在登录的Form组件中添加code字段    
    
# 3.校验登录时候验证码是否正确
    user_input_code = form.cleaned_data.pop('code')
    code = request.session.get('image_code','')
    if code.upper() != user_input_code.upper():
        form.add_error("code","验证码错误")
        return render(request,"login.html",{"form":form})
    request.session.clear()#登录成功后把验证码删掉

#setting.py中
# 4.在url和视图函数的映射中添加这个视图函数和图片url的映射关系

#html文件中
# 5.在html标签中显示图片，地址写该url
<img id="image_code" src="/image/code/" alt="">
"""



import random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
 
def check_code(width=120, height=35, char_length=5, font_file='Monaco.ttf', font_size=28):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')
 
    def rndChar():
        """
        生成随机字母   
        :return:
        """
        flag = random.randint(0, 1)
        if flag == 0:
            return chr(random.randint(48, 57)) # 生成 0 - 9 数字
        return chr(random.randint(65, 90))
 
    def rndColor():
        """
        生成随机颜色
        :return:
        """
        return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))
 
    # 写文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h = random.randint(0, 4)
        draw.text([i * width / char_length, h], char, font=font, fill=rndColor())
 
    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
 
    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor())
 
    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
 
        draw.line((x1, y1, x2, y2), fill=rndColor())
 
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img,''.join(code)
 
"""
if __name__ == '__main__':
    #= 2. 写入文件
    img,code_str = check_code()
    print(code_str)
    with open('code.png','wb') as f:
        img.save(f,format='png')
    pass
"""
