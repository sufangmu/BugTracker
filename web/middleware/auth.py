#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """如果用户已经登录，则在request中赋值"""
        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        request.tracker = user_obj

        # 白名单：如果没有登录也可以访问的url
        # 当前用户访问的白名单，如果在则可以直接访问，如果不存在重定向到登录页面

        if request.path_info in settings.WHITE_URL_REGEX_LIST:
            return
        if not request.tracker:
            return redirect("login")
