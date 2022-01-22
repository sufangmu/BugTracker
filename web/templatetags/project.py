#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django import template
from web import models
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("inclusion/all_project_list.html")
def all_project_list(reqeust):
    user = reqeust.tracker.user
    # 获取我创建的所有项目
    mine = models.Project.objects.filter(creator=user)
    # 获取我参与的所有项目
    join = models.ProjectUser.objects.filter(user=user)
    return {"mine": mine, "join": join}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    menu_list = [
        {"title": "概览", "url": reverse("dashboard", kwargs={"project_id": request.tracker.project.id})},
        {"title": "问题", "url": reverse("issue", kwargs={"project_id": request.tracker.project.id})},
        {"title": "统计", "url": reverse("statistics", kwargs={"project_id": request.tracker.project.id})},
        {"title": "文件", "url": reverse("file", kwargs={"project_id": request.tracker.project.id})},
        {"title": "wiki", "url": reverse("wiki", kwargs={"project_id": request.tracker.project.id})},
        {"title": "设置", "url": reverse("setting", kwargs={"project_id": request.tracker.project.id})},
    ]
    for menu in menu_list:
        if request.path_info.startswith(menu["url"]):
            menu["class"] = "active"

    return {"menu_list": menu_list}
