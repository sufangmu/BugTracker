#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: wiki.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.wiki import WikiModelForm


def wiki(request, project_id):
    return render(request, "wiki.html")


def wiki_add(request, project_id):
    form = WikiModelForm(request)
    if request.method == "POST":
        form = WikiModelForm(request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.save()
            return redirect(reverse('wiki', kwargs={"project_id": project_id}))
    return render(request, "wiki_add.html", {"form": form})


def wiki_catalog(request, project_id):
    """wiki目录"""
    catalog = models.Wiki.objects.filter(project_id=project_id).values("id", "title", "parent")
    return JsonResponse({"status": True, "data": list(catalog)})
