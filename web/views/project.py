#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django.shortcuts import render


def project_list(request):
    return render(request, 'project_list.html')
