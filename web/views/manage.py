#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: manage.py
from django.shortcuts import render


def dashboard(request, project_id):
    return render(request, "dashboard.html")


def statistics(request, project_id):
    return render(request, "statistics.html")
