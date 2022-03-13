from django.shortcuts import render


def setting(request, project_id):
    return render(request, 'setting.html')
