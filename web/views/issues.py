from django.shortcuts import render
from web.forms.issues import IssuesForm


def issue(request, project_id):
    form = IssuesForm()
    return render(request, 'issue.html', {"form": form})
