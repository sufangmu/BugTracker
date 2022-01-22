#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: manage.py
from django.shortcuts import render


def dashboard(request, project_id):
    return render(request, "dashboard.html")


def issue(request, project_id):
    return render(request, "issue.html")


def statistics(request, project_id):
    return render(request, "statistics.html")


def file(request, project_id):
    return render(request, "file.html")


def setting(request, project_id):
    return render(request, "setting.html")
