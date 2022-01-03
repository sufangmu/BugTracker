from django.http import HttpResponse
from django.shortcuts import render
from web.forms.account import RegisterModelForm


def register(request):
    """注册"""
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})


def send_sms(request):
    """发送短信验证码"""
    if request.is_ajax():
        print(request.POST)
    return HttpResponse("ok")