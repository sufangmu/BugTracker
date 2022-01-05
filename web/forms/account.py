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
from web.utils import encrypt

class RegisterModelForm(forms.ModelForm):
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=32,
        error_messages={
            "min_length": "密码长度不能小于8个字符",
            "max_length": "密码长度不能大于32个字符",
        },
        widget=forms.PasswordInput())

    confirm_password = forms.CharField(
        label='重复密码',
        min_length=8,
        max_length=32,
        error_messages={
            "min_length": "密码长度不能小于8个字符",
            "max_length": "密码长度不能大于32个字符",
        },
        widget=forms.PasswordInput())
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
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

    def clean_username(self):
        username = self.cleaned_data["username"]
        exist = models.UserInfo.objects.filter(username=username).exist()
        if exist:
            raise ValidationError("用户名已存在")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        # 对密码进行加密并返回
        password = encrypt.md5(password)
        return password

    def clean_confirm_password(self):
        # self.cleaned_data 已经校验过的数据
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        confirm_password = encrypt.md5(confirm_password)
        if password != confirm_password:
            raise ValidationError("两次密码不一致")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data['email']
        exist = models.UserInfo.objects.filter(email=email).exists()
        if exist:
            raise ValidationError("邮箱已存在")
        return email

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exist:
            raise ValidationError("手机号已注册")
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data['mobile_phone']

        conn = get_redis_connection()
        r_code = conn.get(mobile_phone)
        if not r_code:
            raise ValidationError("验证码失效或未发送，请重新发送")

        r_code = r_code.decode("utf-8")
        if code.strip() != r_code:
            raise ValidationError("验证码错误，请重新输入")
        return code


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
