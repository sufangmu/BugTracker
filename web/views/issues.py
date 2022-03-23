from django.shortcuts import render
from web.forms.issues import IssuesForm
from django.http import JsonResponse
from web import models


def issue(request, project_id):
    if request.method == "GET":
        form = IssuesForm(request)
        issues_obj_list = models.Issues.objects.filter(project_id=project_id)
        return render(request, 'issue.html', {"form": form, "issues": issues_obj_list})

    if request.method == "POST":
        form = IssuesForm(request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.creator = request.tracker.user
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
