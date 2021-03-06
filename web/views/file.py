import json
import requests
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from web.forms.file import FolderModelForm, FileModelForm
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
            "breadcrumb_list": breadcrumb_list,
            "folder_object": parent_object,
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


@csrf_exempt
def cos_credential(request, project_id):
    file_list = json.loads(request.body.decode('utf-8'))
    total_size = 0
    per_file_limit = request.tracker.price_policy.per_file_size * 1024 * 1024
    project_space_limit = request.tracker.price_policy.project_space * 1024 * 1024 * 1024
    for item in file_list:
        if item['size'] > per_file_limit:
            msg = "单文件超出限制(最大{}M，文件：{})".format(request.tracker.price_policy.per_file_size, item["name"])
            return JsonResponse({"status": False, "error": msg})
        else:
            total_size += item["size"]

    use_space = request.tracker.project.use_space
    if use_space + total_size > project_space_limit:
        return JsonResponse({"status": False, "error": "容量超过限制，请升级套餐"})

    """ 获取cos上传临时凭证 """
    data_dict = cos.credential(request.tracker.project.bucket)
    return JsonResponse({"status": True, "data": data_dict})


@csrf_exempt
def file_post(request, project_id):
    """将上传成功的文件写入数据库"""
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过写入数据库
        form.instance.file_type = 1
        form.update_user = request.tracker.user
        # 通过form.save()存储到数据库中的数据返回的instance对象，无法通过get_xxx_display获取choice的值
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({"project": request.tracker.project,
                          "file_type": 1,
                          "update_user": request.tracker.user})
        instance = models.FileRepository.objects.create(**data_dict)

        # 更新项目的已使用空间
        request.tracker.project.use_space += data_dict["file_size"]
        request.tracker.project.save()
        res = {
            "id": instance.id,
            "name": instance.name,
            "file_size": instance.file_size,
            "username": instance.update_user.username,
            "datetime": instance.update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "download_url": reverse("file_download", kwargs={"project_id": project_id, "file_id": instance.id})
        }
        return JsonResponse({"status": True, "data": res})
    # 根据key去COS中获取文件的eTag和前端传递的eTag比较
    return JsonResponse({"status": False, "data": "文件d上传错误"})


def file_download(request, project_id, file_id):
    """下载文件"""
    file_obj = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    file_path = file_obj.file_path
    data = requests.get(file_path).iter_content()  # 大文件分块下载
    response = HttpResponse(data, content_type="application/octet-stream")  # 下载提示框
    # 设置响应头
    # escape_uri_path: 中文名转义
    response["content-Disposition"] = "attachment; filename={}".format(escape_uri_path(file_obj.name))
    return response
