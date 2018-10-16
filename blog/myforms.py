#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__:JasonLIN
from django import forms
from blog.models import UserInfo
from blog import models
from django.forms import widgets
from django.core.exceptions import ValidationError


class UserForm(forms.Form):
    user = forms.CharField(max_length=32,
                           error_messages={'required': '用户不能为空'},
                           label='用户名:',
                           widget=widgets.TextInput(attrs={'class': 'form-control'})
                           )
    
    pwd = forms.CharField(max_length=32,
                          min_length=8,
                          label="密码:",
                          error_messages={'required': '密码不能为空', 'min_length': '密码长度太短,至少8位'},
                          widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    
    re_pwd = forms.CharField(max_length=32,
                             label="确认密码:",
                             error_messages={'required': '确认密码不能为空'},
                             widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    
    email = forms.EmailField(max_length=32,
                             label='邮箱:',
                             error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式不对'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))
    
    def clean_user(self):
        val = self.cleaned_data.get('user')
        user = UserInfo.objects.filter(username=val)
        if user:
            raise ValidationError('该用户名已经注册')
        else:
            return val
    
    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致')
        else:
            return self.cleaned_data
        
    def clean_email(self):
        val = self.cleaned_data.get('email')
        email = UserInfo.objects.filter(email=val)
        if email:
            raise ValidationError('该邮箱已经注册')
        else:
            return val

        
class PasswordForm(forms.Form):
    """
    更改密码单独校验
    """
    pwd = forms.CharField(max_length=32,
                          min_length=8,
                          label="密码:",
                          error_messages={'required': '密码不能为空', 'min_length': '密码长度太短,至少8位'},
                          widget=widgets.PasswordInput(attrs={'class': 'form-control'}))


class EmailForm(forms.Form):
    """
    更改邮箱单独校验
    """
    email = forms.EmailField(max_length=32,
                             label='邮箱:',
                             error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式不对'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))
    
    def clean_email(self):
        val = self.cleaned_data.get('email')
        email = UserInfo.objects.filter(email=val)
        if email:
            raise ValidationError('该邮箱已经注册')
        else:
            return val
        
        

    
        
        
    
    