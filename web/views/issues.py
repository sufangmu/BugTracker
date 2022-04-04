import json

from django.shortcuts import render
from web.forms.issues import IssuesForm, IssuesReplyModelForm
from django.http import JsonResponse
from web import models
from web.utils.pagination import Pagination


def issue(request, project_id):
    if request.method == "GET":
        queryset = models.Issues.objects.filter(project_id=project_id)
        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=10,
        )
        form = IssuesForm(request)
        issues_obj_list = queryset[page_obj.start:page_obj.end]

        return render(request, 'issue.html',
                      {"form": form, "issues": issues_obj_list, "page_html": page_obj.page_html()})

    if request.method == "POST":
        form = IssuesForm(request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.creator = request.tracker.user
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})


def issue_detail(request, project_id, issue_id):
    """编辑问题"""
    issue_obj = models.Issues.objects.filter(project_id=project_id, id=issue_id).first()
    form = IssuesForm(request, instance=issue_obj)
    return render(request, 'issue_detail.html', {"form": form, "issue_obj": issue_obj})


def issue_replies(request, project_id, issue_id):
    """初始化问题评论"""
    if request.method == "GET":
        reply_list = models.IssueReply.objects.filter(issues_id=issue_id, issues__project=request.tracker.project)
        # 格式化queryset为JSON
        data_list = []
        for row in reply_list:
            data = {
                "id": row.id,
                "reply_type_text": row.get_reply_type_display(),
                "content": row.content,
                "creator": row.creator.username,
                "datetime": row.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "parent_id": row.reply_id,
            }
            data_list.append(data)
        return JsonResponse({"status": True, "data": data_list})
    if request.method == "POST":
        form = IssuesReplyModelForm(data=request.POST)
        if form.is_valid():
            form.instance.issues_id = issue_id
            form.instance.reply_type = 2
            form.instance.creator = request.tracker.user
            instance = form.save()
            data = {
                "id": instance.id,
                "reply_type_text": instance.get_reply_type_display(),
                "content": instance.content,
                "creator": instance.creator.username,
                "datetime": instance.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "parent_id": instance.reply_id,
            }
            return JsonResponse({"status": True, "data": data})
        return JsonResponse({"status": False, "error": form.errors})


def issue_change(request, project_id, issue_id):
    issue_obj = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    value = data.get('value')

    field_obj = models.Issues._meta.get_field(name)

    def create_reply_msg(change_msg):
        reply_obj = models.IssueReply.objects.create(
            reply_type=1,
            issues=issue_obj,
            content=change_msg,
            creator=request.tracker.user,
        )
        reply_data = {
            "id": reply_obj.id,
            "reply_type_text": reply_obj.get_reply_type_display(),
            "content": reply_obj.content,
            "creator": reply_obj.creator.username,
            "datetime": reply_obj.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "parent_id": reply_obj.reply_id,
        }
        return reply_data

    # 文本类型字段的更新
    if name in ["subject", "desc", "start_date", "end_date"]:
        if not value:
            if not field_obj.null:  # 数据库中不允许为空
                return JsonResponse({"status": False, "error": "该字段不能为空"})
            setattr(issue_obj, name, None)
            issue_obj.save()
            change_msg = "{}更新为空".format(field_obj.verbose_name)
        else:
            setattr(issue_obj, name, value)
            issue_obj.save()
            change_msg = "{}更新为空{}".format(field_obj.verbose_name, value)

        return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})

    return JsonResponse({})
