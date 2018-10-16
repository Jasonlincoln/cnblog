#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__:JasonLIN

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from django.shortcuts import HttpResponse


def get_random_color():
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))


def get_valid_code_img(request):
    img = Image.new('RGB', (270, 40), color=get_random_color())
    # "RGB" (width, height) color=(255,0,0)三原色
    draw = ImageDraw.Draw(img)
    frestysb_font = ImageFont.truetype("static/font/FRESTYSB.ttf", size=32)
    
    valid_code_str = ''
    
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(65, 90))
        random_upper_alpha = chr(random.randint(97, 122))
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 50, 0), random_char, get_random_color(), font=frestysb_font)
        # 坐标 内容 颜色 字体
        
        # 保存随机字符串
        valid_code_str += random_char
    # width = 270
    # height = 40
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, x2, y1, y2), fill=get_random_color())
    #
    # for i in range(100):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x+4, y+4), 0, 90, fill=get_random_color())
    print(valid_code_str)
    request.session['valid_code_str'] = valid_code_str
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    
    return HttpResponse(data)