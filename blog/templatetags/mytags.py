#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__:JasonLIN
from django import template
from blog import models
from django.db.models import Count
from django.core.paginator import Paginator

register = template.Library()


@register.simple_tag
def multi_tag(x, y):
    return x*y


@register.inclusion_tag('classification.html')
def get_classification_style(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    uncategory_num = len(models.Article.objects.filter(user=user, category__isnull=True).all())
    cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__pk')).values_list('title', 'c')
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__pk')).values_list('title', 'c')
    date_list = models.Article.objects.filter(user=user). \
        extra(select={'Y_m_date': "date_format(create_time, '%%Y-%%m')"}).values('Y_m_date') \
        .annotate(c=Count('pk')).values_list('Y_m_date', 'c')
    
    return {'blog': blog, 'cate_list': cate_list, "user": user,
            'tag_list': tag_list, 'date_list': date_list, "uncategory_num": uncategory_num}



