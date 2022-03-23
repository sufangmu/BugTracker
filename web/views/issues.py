from django.shortcuts import render
from web.forms.issues import IssuesForm
from django.http import JsonResponse


def issue(request, project_id):
    form = IssuesForm(request)
    if request.method == "POST":
        form = IssuesForm(request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
            form.instance.creator = request.tracker.user
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
    return render(request, 'issue.html', {"form": form})
