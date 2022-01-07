from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from web import models
from web.forms.account import RegisterModelForm, SendSMSForm, LoginSMSForm, LoginForm


def index(request):
    return render(request, 'index.html')


def logout(request):
    request.session.flush()
    return redirect('index')


def login(request):
    """用户名和密码登录"""
    form = LoginForm(request)
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user_obj = models.UserInfo.objects.filter(
                Q(username=username) | Q(mobile_phone=username) | Q(email=username)).filter(password=password).first()
            if user_obj:
                request.session['user_id'] = user_obj.id
                request.session.set_expiry(60 * 60 * 24 * 14)
                return redirect('index')
            form.add_error('password', '用户名或密码错误')
        else:
            return render(request, 'login.html', {"form": form})
    return render(request, 'login.html', {"form": form})


def login_sms(request):
    """短信登录"""
    form = LoginSMSForm()
    if request.method == "POST":
        form = LoginSMSForm(request, data=request.POST)
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
    request.session["image_code"] = code
    request.session.set_expiry(60)  # 60失效
    stream = BytesIO()
    img_obj.save(stream, 'png')
    return HttpResponse(stream.getvalue())
