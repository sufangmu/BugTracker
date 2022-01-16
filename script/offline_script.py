#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: offline_script.py
"""
Django 离线脚本
"""
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BugTracker.settings")
django.setup()

from web import models

print(models.UserInfo.objects.all())
