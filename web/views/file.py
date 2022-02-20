from django.forms import model_to_dict
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
        breadcrumb_list = []
        parent = parent_object
        while parent:
            # breadcrumb_list.insert(0, {"id": parent.id, "name": parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ["id", "name"]))
            parent = parent.parent
        # 获取当前当前目录下所欲的文件和文件夹
        queryset = models.FileRepository.objects.filter(project=request.tracker.project)
        if folder_id:
            file_obj_list = queryset.filter(parent=parent_object).order_by("-file_type")
        else:
            # 根路径
            file_obj_list = queryset.filter(parent__isnull=True).order_by("-file_type")
        form = FolderModelForm(request, parent_object)
        context = {
            "form": form,
            "file_obj_list": file_obj_list,
            "breadcrumb_list": breadcrumb_list
        }
        return render(request, "file.html", context)
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
