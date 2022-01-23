#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: wiki.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.wiki import WikiModelForm


def wiki(request, project_id):
    wiki_id = request.GET.get("id")
    if not wiki_id or not wiki_id.isdecimal:
        return render(request, "wiki.html")
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    print(wiki_obj.id, type(wiki_obj.id))
    return render(request, "wiki.html", {"wiki": wiki_obj})


def wiki_delete(request, project_id, wiki_id):
    """删除文档"""
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    return redirect(reverse('wiki', kwargs={"project_id": project_id}))


def wiki_add(request, project_id):
    form = WikiModelForm(request)
    if request.method == "POST":
        form = WikiModelForm(request, data=request.POST)
        if form.is_valid():
            # 判断用户是否已经选择父文档
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            else:
                form.instance.depth = 1
            form.instance.project = request.tracker.project
            form.save()
            return redirect(reverse('wiki', kwargs={"project_id": project_id}))
    return render(request, "wiki_add.html", {"form": form})


def wiki_catalog(request, project_id):
    """wiki目录"""
    catalog = models.Wiki.objects.filter(project_id=project_id).values("id", "title", "parent").order_by("depth", "id")
    return JsonResponse({"status": True, "data": list(catalog)})
