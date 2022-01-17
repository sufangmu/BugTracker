#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: project.py
from django import forms
from django.core.exceptions import ValidationError
from web import models
from web.forms.bootstrap import BootStrapForm


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    """创建项目"""

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = models.Project
        fields = ["name", "color", "desc"]
        widgets = {
            "desc": forms.Textarea(attrs={"style": "resize:none;"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        username = self.request.tracker.user

        # 1. 判断该项目是否已经存在
        exist = models.Project.objects.filter(name=name, creator=username).exists()
        if exist:
            raise ValidationError("该项目已存在")

        # 2. 判断已经创建的项目是否已经到达可用额度上限
        count = models.Project.objects.filter(creator=username).count()

        if count >= self.request.tracker.price_policy.project_num:
            raise ValidationError("可创建项目已达上限")

        return name
