from django.http import HttpResponse
from django.shortcuts import render
from web.forms.account import RegisterModelForm, SendSMSForm


def register(request):
    """注册"""
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})


def send_sms(request):
    """发送短信验证码"""
    if request.is_ajax():
        # 利用form对请求的参数进行校验，将request对象传递给SendSMSForm
        form = SendSMSForm(request, data=request.POST)
        # 校验不为空且格式正确
        if form.is_valid():
            pass
    return HttpResponse("ok")
