from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from web.forms.account import RegisterModelForm, SendSMSForm, LoginSMSForm, LoginForm


def index(request):
    return HttpResponse("index")


def login(request):
    """用户名和密码登录"""
    form = LoginForm()
    return render(request, 'login.html', {"form": form})


def login_sms(request):
    """短信登录"""
    form = LoginSMSForm()
    if request.method == "POST":
        form = LoginSMSForm(data=request.POST)
        if form.is_valid():
            return JsonResponse({"status": True, "url": reverse('index')})
        else:
            return JsonResponse({"status": False, "error": form.errors})
    return render(request, 'login_sms.html', {"form": form})


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


def image_code(request):
    from io import BytesIO
    from web.utils.image_code import check_code
    img_obj, code = check_code()
    print(code)
    stream = BytesIO()
    img_obj.save(stream, 'png')
    return HttpResponse(stream.getvalue())
