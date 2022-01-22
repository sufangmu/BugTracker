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

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        choice_list = [("", "请选择"), ]
        wiki_obj = models.Wiki.objects.filter(project=self.request.tracker.project).values_list("id", "title")
        choice_list.extend(wiki_obj)
        self.fields["parent"].choices = choice_list
