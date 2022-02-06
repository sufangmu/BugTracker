#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: wiki.py
import uuid
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from web import models
from web.forms.wiki import WikiModelForm
from web.utils.tencent import cos


def wiki(request, project_id):
    wiki_id = request.GET.get("id")
    if not wiki_id or not wiki_id.isdecimal:
        return render(request, "wiki.html")
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, "wiki.html", {"wiki": wiki_obj})


def wiki_delete(request, project_id, wiki_id):
    """删除文档"""
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    return redirect(reverse('wiki', kwargs={"project_id": project_id}))


def wiki_edit(request, project_id, wiki_id):
    """编辑文档"""
    wiki_obj = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_id:
        return redirect(reverse('wiki', kwargs={"project_id": project_id}))
    form = WikiModelForm(request, instance=wiki_obj)
    if request.method == "POST":
        form = WikiModelForm(request, data=request.POST, instance=wiki_obj)
        if form.is_valid():
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            else:
                form.instance.depth = 1
            form.save()
            return redirect(reverse('wiki', kwargs={"project_id": project_id}) + "?id=" + wiki_id)
    return render(request, 'wiki_form.html', {"form": form})


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
    return render(request, "wiki_form.html", {"form": form})


@csrf_exempt
def wiki_upload(request, project_id):
    """上传图片"""
    res = {
        "success": 0,
        "message": None,
        "url": None,
    }
    file_obj = request.FILES.get("editormd-image-file")
    if not file_obj:
        res["message"] = "文件不存在"
        return JsonResponse(res)
    bucket = request.tracker.project.bucket
    # 文件上传到桶中
    file_suffix = file_obj.name.rsplit(".")[-1]
    file_name = "{}.{}".format(uuid.uuid4(), file_suffix)
    url = cos.upload_file(bucket, file_obj, file_name)
    res["success"] = 1
    res["url"] = url
    return JsonResponse(res)


def wiki_catalog(request, project_id):
    """wiki目录"""
    catalog = models.Wiki.objects.filter(project_id=project_id).values("id", "title", "parent").order_by("depth", "id")
    return JsonResponse({"status": True, "data": list(catalog)})
