from django.shortcuts import render, redirect
from web.utils.tencent import cos
from web import models
def setting(request, project_id):
    return render(request, 'setting.html')


def delete(request, project_id):
    if request.method == "GET":
        return render(request, 'setting_delete.html')

    project_name = request.POST.get("project_name")
    # 判断项目名是否合法
    if not project_name or project_name != request.tracker.project.name:
        return render(request, "setting_delete.html", {"error": "项目名错误"})

    # 只有创建者可以删除
    if request.tracker.user != request.tracker.project.creator:
        return render(request, "setting_delete.html", {"error": "需要创建者删除"})
    # 删除COS桶
    cos.delete_bucket(request.tracker.project.bucket)
    models.Project.objects.filter(id=project_id).delete()
    # 删除项目
    return redirect("project_list")
