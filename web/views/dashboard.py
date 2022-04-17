#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from django.http import JsonResponse
from django.shortcuts import render
from web import models
from django.db.models import Count
import collections
import datetime
import time


def dashboard(request, project_id):
    """概览"""
    status_dict = collections.OrderedDict()
    for key, value in models.Issues.status_choices:
        status_dict[key] = {"text": value, "count": 0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values("status").annotate(count=Count("id"))
    for item in issues_data:
        status_dict[item["status"]]["count"] = item["count"]

    # 项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values("user_id", "user__username")

    # 最近的10个问题
    top_ten = models.Issues.objects.filter(project_id=project_id, assign_id__isnull=False).order_by("-id")[0:10]

    context = {
        "status_dict": status_dict,
        "user_list": user_list,
        "top_ten": top_ten,
    }
    return render(request, "dashboard.html", context)


def issues_chart(request, project_id):
    """在概览中生成highchart所需的数据"""
    # 最近30天每天创建的问题数量
    today = datetime.datetime.now().date()
    date_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        print(date)
        date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    result = models.Issues.objects.filter(project_id=project_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={"ctime": "DATE_FORMAT(web_issues.create_datetime, '%%Y-%%m-%%d')"}).values('ctime').annotate(
        ct=Count('id'))  # <QuerySet [{'ctime': '2022-04-10', 'ct': 1}, {'ctime': '2022-04-17', 'ct': 2}]>
    for item in result:
        date_dict[item["ctime"]][1] = item["ct"]

    return JsonResponse({"status": True, "data": list(date_dict.values())})
