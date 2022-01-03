#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from django.urls import path
from web.views import account
urlpatterns = [
    path('register/', account.register, name='register'),
    path('send_sms/', account.send_sms, name='send_sms'),
]