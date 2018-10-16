"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from blog import views
from cnblog import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('', views.index),
    path('get_valid_code_img/', views.get_valid_code_img),
    path('register/', views.register),
    path('index/', views.index),
    path('logout/', views.logout),
    path("digg/", views.digg),
    path('comment/', views.comment),
    path('get_comment_tree/', views.get_comment_tree),
    path("email_settings/", views.email_settings),
    path("password_settings/", views.password_settings),
    path("avatar_settings/", views.avatar_settings),
    
    # 后台管理
    path("cn_backend/", views.cn_backend),
    path("cn_backend/add-article/", views.add_article),
    path("cn_backend/add-category/", views.add_category),
    path("upload/", views.upload),
    path("edit_category/", views.edit_category),
    re_path("delete_category/(\d+)/$", views.delete_category),
    re_path("cn_backend/(\d+)/delete_article/$", views.delete_article),
    re_path("cn_backend/(\d+)/edit_article/$", views.edit_article),
    re_path(r'edit/(?P<param>\w+)/$', views.filter_category),
    
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path('^(?P<username>\w+)/$', views.home_site),
    re_path(r"^(?P<username>\w+)/articles/(?P<article_id>\d+)$", views.article_detail),
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),
    
   

]
