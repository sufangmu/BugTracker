#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django import template
from web import models

register = template.Library()


@register.inclusion_tag("inclusion/all_project_list.html")
def all_project_list(reqeust):
    user = reqeust.tracker.user
    # 获取我创建的所有项目
    mine = models.Project.objects.filter(creator=user)
    # 获取我参与的所有项目
    join = models.ProjectUser.objects.filter(user=user)
    return {"mine": mine, "join": join}
