from django.http import JsonResponse
from django.shortcuts import render
from web.forms.file import FolderModelForm
from web import models


def file(request, project_id):
    """获取文件列表、添加文件夹"""
    parent_object = None
    folder_id = request.GET.get("folder", "")
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracker.project).first()

    if request.method == "GET":
        form = FolderModelForm(request, parent_object)
        return render(request, "file.html", {"form": form})
    if request.method == "POST":
        form = FolderModelForm(request, parent_object, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.update_user = request.tracker.user
            form.instance.file_type = 2
            form.instance.parent = parent_object
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
