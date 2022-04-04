from django.shortcuts import render
from web.forms.issues import IssuesForm
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
    return render(request, 'issue_detail.html', {"form": form})


def issue_replies(request, project_id, issue_id):
    """初始化问题评论"""
    reply_list = models.Issuereply.objects.filter(issue_id=issue_id, issues__project=request.tracker.project)
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
