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
