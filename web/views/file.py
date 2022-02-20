from django.http import JsonResponse
from django.shortcuts import render
from web.forms.file import FolderModelForm


def file(request, project_id):
    """获取文件列表、添加文件夹"""
    if request.method == "GET":
        form = FolderModelForm()
        return render(request, "file.html", {"form": form})
    if request.method == "POST":
        form = FolderModelForm(request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.update_user = request.tracker.user
            form.instance.file_type = 2
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
