#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: wiki.py

from django import forms
from web import models
from web.forms.bootstrap import BootStrapForm


class WikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        fields = ["title", "content", "parent"]
        # exclude = ["project"]
