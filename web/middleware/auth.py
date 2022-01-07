#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

from django.utils.deprecation import MiddlewareMixin
from web import models


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """如果用户已经登录，则在request中赋值"""
        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        request.tracker = user_obj
