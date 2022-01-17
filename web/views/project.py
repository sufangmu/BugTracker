#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django.http import JsonResponse
from django.shortcuts import render
from web.forms.project import ProjectModelForm


def project_list(request):
    if request.method == "GET":
        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {"form": form})
    if request.method == "POST":
        form = ProjectModelForm(request, data=request.POST)
        if form.is_valid():
            # Project中creator是必须要有的字段，此处需要添加上
            form.instance.creator = request.tracker.user
            form.save()
            # 由于是ajax请求，所以返回json字符串
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
