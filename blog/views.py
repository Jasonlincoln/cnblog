from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Count
import json
import os
import threading
from django.core.mail import send_mail
from bs4 import BeautifulSoup
from blog.utils import valid_code
from blog.myforms import UserForm
from blog.myforms import PasswordForm
from blog.myforms import EmailForm
from blog.models import UserInfo
from blog import models
from cnblog import settings

from django.core.paginator import Paginator, EmptyPage


# Create your views here.


def login(request):
    if request.method == "POST":
        response = {"user": None, "msg": None}
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        get_valid_code = request.POST.get('valid_code')
        
        valid_code_str = request.session.get('valid_code_str')
        if get_valid_code.upper() == valid_code_str.upper():
            
            user = auth.authenticate(username=user, password=pwd)
            if user:
                # 注册登录 request.user == 当前对象
                auth.login(request, user)
                response["user"] = user.username
            
            else:
                response["msg"] = "用户名或者密码错误"
        
        else:
            response["msg"] = "验证码是错误"
        
        return JsonResponse(response)
    return render(request, 'login.html')


def get_valid_code_img(request):
    return valid_code.get_valid_code_img(request)


def register(request):
    """
    注册视图函数
    :param request:
    :return:
    """
    if request.is_ajax():
        form = UserForm(request.POST)
        response = {"uer": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")
            
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            response["msg"] = form.errors
        return JsonResponse(response)
    
    form = UserForm()
    return render(request, "register.html", {"form": form})


def get_num_pages(paginator, current_page_num):
    """
    计算分页
    :param paginator:
    :param current_page_num:
    :return: page_range
    """
    num_pages = paginator.num_pages
    if paginator.num_pages > 11:
        if current_page_num - 5 < 1:
            page_range = range(1, 12)
        elif current_page_num + 5 > num_pages:
            page_range = range(num_pages - 10, num_pages + 1)
        else:
            page_range = range(current_page_num - 5, current_page_num + 6)
    else:
        page_range = paginator.page_range
    return page_range


def index(request):
    article_list = models.Article.objects.all()
    paginator = Paginator(article_list, 2)
    current_page_num = int(request.GET.get("page", 1))
    current_page = paginator.page(current_page_num)
    page_range = get_num_pages(paginator, current_page_num)
    
    return render(request, 'index.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def get_num_pages(paginator, current_page_num):
    """
    计算分页
    :param paginator:
    :param current_page_num:
    :return: page_range
    """
    num_pages = paginator.num_pages
    if paginator.num_pages > 11:
        if current_page_num - 5 < 1:
            page_range = range(1, 12)
        elif current_page_num + 5 > num_pages:
            page_range = range(num_pages - 10, num_pages + 1)
        else:
            page_range = range(current_page_num - 5, current_page_num + 6)
    else:
        page_range = paginator.page_range
    return page_range


def home_site(request, username, **kwargs):
    """
    个人站点视图
    :param request:
    :param username:
    :param kwargs: {condition:tag, param:2018-7}
    :return:
    """
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'not_found.html')
    article_list = models.Article.objects.filter(user=user)
    blog = user.blog
    
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'tag':
            article_list = article_list.filter(tags__title=param)
        elif condition == 'category':
            if param == "null":
                article_list = article_list.filter(category__isnull=True)
            else:
                article_list = article_list.filter(category__title=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    paginator = Paginator(article_list, 8)
    current_page_num = int(request.GET.get("page", 1))
    current_page = paginator.page(current_page_num)
    page_range = get_num_pages(paginator, current_page_num)
    return render(request, 'home_site.html', locals())


def article_detail(request, username, article_id):
    """文章详情页面"""
    
    article_obj = models.Article.objects.filter(nid=article_id).first()
    
    comment_list = models.Comment.objects.filter(article_id=article_id).all()
    
    paginator = Paginator(comment_list, 8)
    current_page_num = int(request.GET.get("page", 1))
    current_page = paginator.page(current_page_num)
    page_range = get_num_pages(paginator, current_page_num)
    
    return render(request, 'article_detail.html', locals())


def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """
    response = {"state": True}
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user_id = request.user.pk
    obj = models.ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id).first()
    
    if not obj:  # 没点过赞或者没踩过
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        queryset = models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    
    else:
        response["state"] = False
        response["handled"] = obj.is_up
    return JsonResponse(response)


def comment(request):
    """
    评论
    :param request:
    :return:
    """
    user_id = request.user.pk
    content = request.POST.get('content')
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    article_obj = models.Article.objects.filter(pk=article_id)
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, content=content, article_id=article_id,
                                                    parent_comment_id=pid)
        article_obj.update(comment_count=F("comment_count") + 1)
    
    create_time = comment_obj.create_time.strftime("%Y-%m-%d %X")
    username = comment_obj.user.username
    content = comment_obj.content
    response = {"create_time": create_time, "username": username, "content": content}
    
    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    
    comment_list = list(models.Comment.objects.filter(article_id=article_id).order_by('pk').
                        values('pk', 'content', 'parent_comment_id'))
    return JsonResponse(comment_list, safe=False)


def to_send_mail(article_obj, content):
    """
    发邮件
    :param article_obj: QuerySet
    :param content:
    :return:
    """
    title = "您的文章[%s],新增了一条评论内容" % article_obj.title
    recipient = article_obj.user.email
    t = threading.Thread(target=send_mail,
                         args=(title,
                               content,
                               settings.EMAIL_HOST_USER,
                               [recipient])
                         )
    t.start()


@login_required
def cn_backend(request):
    """
    后台管理首页
    :param request:
    :return:
    """
    user = request.user
    article_list = models.Article.objects.filter(user=user).all()
    category_list = models.Category.objects.filter(blog=user.blog)\
        .annotate(c=Count("article__pk")).values_list("title", "c")

    uncategory_num = len(models.Article.objects.filter(user=user, category__isnull=True).all())

    paginator = Paginator(article_list, 8)
    current_page_num = int(request.GET.get("page", 1))
    current_page = paginator.page(current_page_num)
    page_range = get_num_pages(paginator, current_page_num)
    return render(request, "backend/cn_backend.html", locals())


@login_required
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    user = request.user
    category_list = models.Category.objects.filter(blog=user.blog).annotate(c=Count("article__pk")) \
        .values_list("title", "c", "pk")
    if request.method == "POST":
        content = request.POST.get('content')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        title = str(filter_content(title))
        soup = filter_content(content)
        desc = get_desc(soup)
        
        content = str(soup)
        extra = {}
        if category_id:
            extra["category_id"] = category_id
        models.Article.objects.create(title=title, desc=desc, content=content, user=request.user,
                                      **extra)
        return redirect("/cn_backend/")
    return render(request, 'backend/add_article.html', locals())


def get_desc(soup):
    """
    格式化desc 文章摘要
    :param: soup
    :return: desc
    """
    if len(soup.text) <= 150:
        desc = soup.text
    else:
        desc = soup.text[0: 150] + "..."
    return desc


def filter_content(content):
    """
    过滤script标签
    :param content:
    :return: soup
    """
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.find_all():
        if tag.name == "script":
            tag.decompose()
    return soup


@login_required
def edit_article(request, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    user = request.user
    category_list = models.Category.objects.filter(blog=user.blog).all()
    uncategory_num = len(models.Article.objects.filter(user=user, category__isnull=True).all())
    if request.method == "POST":
        content = request.POST.get('content')
        title = request.POST.get('title')
        title = str(filter_content(title))
        soup = filter_content(content)
        desc = get_desc(soup)
        content = str(soup)
        models.Article.objects.filter(pk=article_id).update(title=title, desc=desc, content=content, user=request.user,
                                                            category_id=2)
        return redirect("/cn_backend/")
    
    return render(request, 'backend/edit_article.html', locals())


@login_required
def delete_article(request, article_id):
    models.Article.objects.filter(pk=article_id).delete()
    return redirect('/cn_backend/')


def filter_category(request, param):
    """
    过滤分类
    :param request:
    :param param:filter
    :return:
    """
    blog = request.user.blog
    uncategory_num = len(models.Article.objects.filter(user=request.user, category__isnull=True).all())
    if param == "null":
        article_list = models.Article.objects.filter(user=request.user, category__isnull=True).all()
    else:
        category = models.Category.objects.filter(title=param, blog=blog).first()
        article_list = models.Article.objects.filter(category__pk=category.pk).all()
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__pk")) \
        .values_list("title", "c")
    return render(request, 'backend/filter_category.html', locals())


def edit_category(request):
    """
    :param request:
    :param category_id:
    :return:
    """
    blog = request.user.blog
    uncategory_num = len(models.Article.objects.filter(user=request.user, category__isnull=True).all())
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__pk")) \
        .values_list("title", "c", "pk")
    return render(request, "backend/edit_category.html", locals())


def category_form(request, category):
    """
    校验category合法性
    :param request:
    :param category:
    :return: response
    """
    response = {"user": None, "msg": None}
    obj = models.Category.objects.filter(blog=request.user.blog, title=category)
    if len(category) - len(category.replace(" ", "")) > 0:
        response["msg"] = "分类名称不能包含空格"
    elif obj:
        response["msg"] = "该分类已经存在"
    return response


def add_category(request):
    blog = request.user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article__pk")) \
        .values_list("title", "c", "pk")
    if request.is_ajax():
        category = request.POST.get("category")
        response = category_form(request, category)
        if response.get("msg"):
            return JsonResponse(response)
        else:
            models.Category.objects.create(blog=blog, title=category)
            response["user"] = request.user.username
        return JsonResponse(response)
    
    return render(request, "backend/add_category.html", locals())


def delete_category(request, category_id):
    """
    删除文章分类
    :param request:
    :param category_id:
    :return:
    """
    models.Category.objects.filter(pk=category_id).delete()
    return redirect('/edit_category/')


def upload(request):
    """
    编辑器上传文件
    :param request:
    :return:
    """
    img_obj = request.FILES.get("upload_img")
    
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)
    with open(path, "wb")as f:
        for line in img_obj:
            f.write(line)
    return HttpResponse("上传成功")


def email_settings(request):
    """
    用户信息更改
    :param request:
    :return:
    """
    if request.is_ajax():
        user = request.user
        form = EmailForm(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            email = form.cleaned_data.get("email")
            
            models.UserInfo.objects.filter(pk=user.pk).update(email=email)
            response["user"] = user.username
        
        else:
            print(form.errors)
            response["msg"] = form.errors
        
        return JsonResponse(response)
    
    return render(request, 'email_settings.html', locals())


def password_settings(request):
    if request.is_ajax():
        user = request.user
        response = {"user": None, "msg": None}
        form = PasswordForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data.get("pwd")
            models.UserInfo.objects.filter(pk=user.pk).update(password=make_password(pwd))
            response["user"] = user.username
        else:
            response["msg"] = form.errors
        return JsonResponse(response)
    return render(request, "password_settings.html", locals())


def avatar_settings(request):
    if request.is_ajax():
        response = {"user": None, "msg": None}
        avatar_obj = request.FILES.get('avatar')
        if avatar_obj is None:
            response["msg"] = "头像为空"
        else:
            avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars", str(avatar_obj))
            with open(avatar_path, "wb")as f:
                for line in avatar_obj:
                    f.write(line)
            models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=avatar_path)
            response["user"] = request.user.username
        return JsonResponse(response)
    return render(request, 'avatar_settings.html', locals())
