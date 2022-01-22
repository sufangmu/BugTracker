#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import datetime
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings


class Tracker:
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):

        request.tracker = Tracker()
        """如果用户已经登录，则在request中赋值"""
        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        request.tracker.user = user_obj

        # 白名单：如果没有登录也可以访问的url
        # 当前用户访问的白名单，如果在则可以直接访问，如果不存在重定向到登录页面

        if request.path_info in settings.WHITE_URL_REGEX_LIST:
            return
        if not request.tracker.user:
            return redirect("login")

        # 登录成功以后
        # 获取当前用户ID最大的交易记录
        obj = models.Transaction.objects.filter(user=user_obj, status=2).order_by("-id").first()
        # 判断是否已过期
        current_datetime = datetime.datetime.now()
        if obj.end_datetime and obj.end_datetime < current_datetime:
            obj = models.Transaction.objects.filter(user=user_obj, status=2, price_policy__catepory=1).order_by(
                "id").first()
        request.tracker.price_policy = obj.price_policy

    def process_view(self, request, view, args, kwargs):
        """路由匹配之后，视图函数之前"""

        # 判断URL是否是以manage开头
        if not request.path_info.startswith("/manage/"):
            return
        project_id = kwargs.get("project_id")
        # 判断project_id 是否是我创建的或我参与的
        user = request.tracker.user
        project_obj = models.Project.objects.filter(creator=user, id=project_id).first()
        if project_obj:
            request.tracker.project = project_obj
            return
        project_user_obj = models.ProjectUser.objects.filter(user=user, id=project_id).first()
        if project_user_obj:
            request.tracker.project = project_user_obj.project
            return

        return redirect('project_list')
