from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from web.forms.account import RegisterModelForm, SendSMSForm


def login(request):
    return HttpResponse("ok")


def register(request):
    """注册"""
    form = RegisterModelForm()
    if request.method == 'POST':
        form = RegisterModelForm(data=request.POST)
        if form.is_valid():
            form.save()  # save()会自动剔除表中不存在的字段
            return JsonResponse({"status": True, "url": reverse('login')})
        return JsonResponse({"status": False, "error": form.errors})
    return render(request, 'register.html', {'form': form})


def send_sms(request):
    """发送短信验证码"""
    if request.is_ajax():
        # 利用form对请求的参数进行校验，将request对象传递给SendSMSForm
        form = SendSMSForm(request, data=request.POST)
        # 校验不为空且格式正确
        if form.is_valid():
            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})
