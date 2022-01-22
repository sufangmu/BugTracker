#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: wiki.py
from django.shortcuts import render


def wiki(request, project_id):
    return render(request, "wiki.html")
