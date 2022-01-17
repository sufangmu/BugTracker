#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django.http import JsonResponse
from django.shortcuts import render
from web.forms.project import ProjectModelForm
from web import models


def project_list(request):
    """项目列表"""
    # 1. 从数据库中获取两部分数据
    #     我创建的所有项目：已星标、未星标
    #     我参与的所有项目：已星标、未星标
    # 2. 提取已星标
    #     列表 = 循环 [我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取
    #
    # 得到三个列表：星标、创建、参与
    if request.method == "GET":
        user = request.tracker.user
        project_dict = {"star": [], "mine": [], "join": []}
        # 获取我创建的项目
        my_project_list = models.Project.objects.filter(creator=user)
        for item in my_project_list:
            if item.star:
                project_dict["star"].append(item)
            else:
                project_dict["mine"].append(item)
        # 获取我参与的项目
        join_project_list = models.ProjectUser.objects.filter(user=user)
        for item in join_project_list:
            if item.star:
                project_dict["star"].append(item.project)
            else:
                project_dict["join"].append(item.project)
        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {"form": form, "projects": project_dict})
    if request.method == "POST":
        form = ProjectModelForm(request, data=request.POST)
        if form.is_valid():
            # Project中creator是必须要有的字段，此处需要添加上
            form.instance.creator = request.tracker.user
            form.save()
            # 由于是ajax请求，所以返回json字符串
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
