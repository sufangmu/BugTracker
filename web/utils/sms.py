#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: sms.py
# 测试用发送信息
from django.conf import settings


def send_single_sms(mobile_phone, template, content):
    print(mobile_phone, settings.SMS_TEMPLATES[template], content)
    return {"status": "success"}
