#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
import time
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from web.forms.project import ProjectModelForm
from web import models
from web.utils.tencent import cos
from django.conf import settings


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
                item.type = "mine"
                project_dict["star"].append(item)
            else:
                project_dict["mine"].append(item)
        # 获取我参与的项目
        join_project_list = models.ProjectUser.objects.filter(user=user)
        for item in join_project_list:
            if item.star:
                item.project.type = "join"
                project_dict["star"].append(item.project)
            else:
                project_dict["join"].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {"form": form, "projects": project_dict})
    if request.method == "POST":
        form = ProjectModelForm(request, data=request.POST)
        if form.is_valid():
            # 为项目创建桶，同名中必须包含TENCENT_APP_ID
            bucket = "{}-{}-{}".format(request.tracker.user.mobile_phone, str(int(time.time())),
                                       settings.TENCENT_APP_ID)
            cos.create_bucket(bucket)
            form.instance.bucket = bucket
            # Project中creator是必须要有的字段，此处需要添加上
            form.instance.creator = request.tracker.user
            instance = form.save()
            # 创建项目时初始化Issue中的问题类型
            issue_type_obj_list = []
            for item in models.IssueType.ISSUE_TYPE_INIT_LIST:
                issue_type_obj_list.append(models.IssueType(project=instance, title=item))
                # 由于是ajax请求，所以返回json字符串
            models.IssueType.objects.bulk_create(issue_type_obj_list)
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})


def project_star(request, project_type, project_id):
    """星标"""
    if project_type == "mine":
        models.Project.objects.filter(id=project_id, creator=request.tracker.user).update(star=True)
        return redirect("project_list")
    elif project_type == "join":
        models.ProjectUser.objects.filter(id=project_id, user=request.tracker.user).update(star=True)
        return redirect("project_list")
    return HttpResponse('请求错误')


def project_unstar(request, project_type, project_id):
    """取消星标"""
    if project_type == "mine":
        models.Project.objects.filter(id=project_id, creator=request.tracker.user).update(star=False)
        return redirect("project_list")
    elif project_type == "join":
        models.ProjectUser.objects.filter(id=project_id, user=request.tracker.user).update(star=False)
        return redirect("project_list")
    return HttpResponse('请求错误')
