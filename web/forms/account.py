#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import random
from django import forms
from django_redis import get_redis_connection
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from web import models
from django.conf import settings
from web.utils.sms import send_single_sms


class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput())

    confirm_password = forms.CharField(
        label='重复密码',
        widget=forms.PasswordInput())
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        fields = ['username', 'password', 'confirm_password', 'email', 'mobile_phone', 'code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)


class SendSMSForm(forms.Form):
    """利用form校验手机号"""
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # 校验手机号是否存在的钩子
    def clean_mobile_phone(self):
        template = self.request.POST.get("template")
        if not settings.SMS_TEMPLATES.get(template):
            raise ValidationError("短信模板不存在")
        mobile_phone = self.cleaned_data["mobile_phone"]
        # 校验数据库中是否已有手机号
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exist:
            raise ValidationError("手机号已存在")

        # 生成随机验证码并发送短信
        code = random.randrange(1000, 9999)
        result = send_single_sms(mobile_phone, template, [code, ])
        if result["status"] != "success":
            raise ValidationError("短信发送失败")

        # 验证码写入Redis(django-redis)
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)
        return mobile_phone
