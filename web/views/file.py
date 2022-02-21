import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from web.forms.file import FolderModelForm
from web import models
from web.utils.tencent import cos


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
        fid = request.POST.get("fid", '')
        edit_obj = None
        if fid.isdecimal():
            edit_obj = models.FileRepository.objects.filter(id=int(fid), file_type=2,
                                                            project=request.tracker.project).first()
        if edit_obj:
            form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_obj)
        else:
            form = FolderModelForm(request, parent_object, data=request.POST)

        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.update_user = request.tracker.user
            form.instance.file_type = 2
            form.instance.parent = parent_object
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})


def file_delete(request, project_id):
    fid = request.GET.get("fid")
    delete_obj = models.FileRepository.objects.filter(id=fid, project=request.tracker.project).first()
    if delete_obj.file_type == 1:
        # 删除文件
        # 释放空间
        request.tracker.project.use_space -= delete_obj.file_size
        request.tracker.project.save()
        # 删除COS中的文件
        cos.delete_file(request.tracker.project.bucket, delete_obj.key)
        # 删除数据库中的记录
        delete_obj.delete()
    else:
        # 删除目录
        total_size = 0
        key_list = []
        folder_list = [delete_obj, ]
        for folder in folder_list:
            child_list = models.FileRepository.objects.filter(project=request.tracker.project, parent=folder).order_by(
                "-file_type")
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    total_size += child.file_size
                    key_list.append({"Key": child.key})
            # 批量删除文件
            if key_list:
                cos.delete_files(request.tracker.project.bucket, child.key)
            # 归还容量
            if total_size:
                request.tracker.project.use_space -= total_size
                request.tracker.project.save()
        delete_obj.delete()
        return JsonResponse({"status": True})


def cos_credential(request, project_id):
    """ 获取cos上传临时凭证 """
    data_dict = cos.credential(request.tracker.project.bucket)
    return JsonResponse(data_dict)
