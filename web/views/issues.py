import json

from django.shortcuts import render
from django.utils.safestring import mark_safe

from web.forms.issues import IssuesForm, IssuesReplyModelForm
from django.http import JsonResponse
from web import models
from web.utils.pagination import Pagination


class CheckFilter:
    def __init__(self, name, data, request):
        self.name = name
        self.data = data
        self.request = request

    def __iter__(self):
        for item in self.data:
            key = str(item[0])
            value = item[1]
            checked = ""
            # 如果当前用户请求的URL中status的值和当前循环key相等 checked = "checked"
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                checked = "checked"
            html = '<a class="cell" href="#"><input type="checkbox" {checked} /><label>{value}</label></a>'.format(
                value=value, checked=checked)
            yield mark_safe(html)


def issue(request, project_id):
    # 筛选
    allow_filter_name = ["issues_type", "status", "priority"]
    condition = {}
    for name in allow_filter_name:
        value_list = request.GET.getlist(name)
        if not value_list:
            continue
        condition["{}__in".format(name)] = value_list

    if request.method == "GET":
        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
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
                      {
                          "form": form,
                          "issues": issues_obj_list,
                          "page_html": page_obj.page_html(),
                          "filter_list": [
                              {"title": "状态", "filter": CheckFilter("status", models.Issues.status_choices, request)},
                              {"title": "优先级",
                               "filter": CheckFilter("priority", models.Issues.priority_choices, request)},
                          ]
                      })
    if request.method == "POST":
        form = IssuesForm(request, data=request.POST)
        if form.is_valid():
            form.instance.project = request.tracker.project
        form.instance.creator = request.tracker.user
        form.save()
        return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})


def issue_detail(request, project_id, issue_id):
    """编辑问题"""
    issue_obj = models.Issues.objects.filter(project_id=project_id, id=issue_id).first()
    form = IssuesForm(request, instance=issue_obj)
    return render(request, 'issue_detail.html', {"form": form, "issue_obj": issue_obj})


def issue_replies(request, project_id, issue_id):
    """初始化问题评论"""
    if request.method == "GET":
        reply_list = models.IssueReply.objects.filter(issues_id=issue_id, issues__project=request.tracker.project)
        # 格式化queryset为JSON
        data_list = []
        for row in reply_list:
            data = {
                "id": row.id,
                "reply_type_text": row.get_reply_type_display(),
                "content": row.content,
                "creator": row.creator.username,
                "datetime": row.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "parent_id": row.reply_id,
            }
            data_list.append(data)
        return JsonResponse({"status": True, "data": data_list})
    if request.method == "POST":
        form = IssuesReplyModelForm(data=request.POST)
        if form.is_valid():
            form.instance.issues_id = issue_id
            form.instance.reply_type = 2
            form.instance.creator = request.tracker.user
            instance = form.save()
            data = {
                "id": instance.id,
                "reply_type_text": instance.get_reply_type_display(),
                "content": instance.content,
                "creator": instance.creator.username,
                "datetime": instance.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "parent_id": instance.reply_id,
            }
            return JsonResponse({"status": True, "data": data})
        return JsonResponse({"status": False, "error": form.errors})


def issue_change(request, project_id, issue_id):
    issue_obj = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    value = data.get('value')

    field_obj = models.Issues._meta.get_field(name)

    def create_reply_msg(msg):
        reply_obj = models.IssueReply.objects.create(
            reply_type=1,
            issues=issue_obj,
            content=msg,
            creator=request.tracker.user,
        )
        reply_data = {
            "id": reply_obj.id,
            "reply_type_text": reply_obj.get_reply_type_display(),
            "content": reply_obj.content,
            "creator": reply_obj.creator.username,
            "datetime": reply_obj.create_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "parent_id": reply_obj.reply_id,
        }
        return reply_data

    # 文本类型字段的更新
    if name in ["subject", "desc", "start_date", "end_date"]:
        if not value:
            if not field_obj.null:  # 数据库中不允许为空
                return JsonResponse({"status": False, "error": "该字段不能为空"})
            setattr(issue_obj, name, None)
            issue_obj.save()
            change_msg = "{}更新为空".format(field_obj.verbose_name)
        else:
            setattr(issue_obj, name, value)
            issue_obj.save()
            change_msg = "{}更新为{}".format(field_obj.verbose_name, value)

        return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})
    # 外键字段更新, 如果是指派要判断是否是创建者或者是参与者
    if name in ["issues_type", "module", "parent", "assign"]:
        # 用户选择为空
        if not value:
            if not field_obj.null:
                return JsonResponse({"status": False, "error": "该字段不能为空"})
            # 允许为空
            setattr(issue_obj, name, None)
            issue_obj.save()
            change_msg = "{}更新为空".format(field_obj.verbose_name)
        # 用户输入不为空
        else:
            if name == "assign":
                # 判断是否是创建者
                if value == str(request.tracker.project.creator_id):
                    instance = request.tracker.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({"status": False, "error": "选择的值不存在"})
                setattr(issue_obj, name, instance)
                issue_obj.save()
                change_msg = "{}更新为{}".format(field_obj.verbose_name, str(instance))
                return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})

                # 是否是项目参与者
            else:
                # 条件判断： 用户输入的值时自己的值
                instance = field_obj.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({"status": False, "error": "选择的值不存在"})
                setattr(issue_obj, name, instance)
                issue_obj.save()
                change_msg = "{}更新为{}".format(field_obj.verbose_name, str(instance))
                return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})
    # choices字段更新
    if name in ["priority", "status", "mode"]:
        selected_text = None
        for key, text in field_obj.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({"status": False, "error": "选择的值不存在"})
        setattr(issue_obj, name, value)
        issue_obj.save()
        change_msg = "{}更新为{}".format(field_obj.verbose_name, selected_text)
        return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})
    # manytomany字段更新
    if name in ["attention"]:
        if not isinstance(value, list):
            return JsonResponse({"status": False, "error": "数据格式错误"})
        if not value:
            # 关注列表为空
            issue_obj.attention.set(value)
            issue_obj.save()
            change_msg = "{}更新为空".format(field_obj.verbose_name)
        else:
            # 判断列关注者是否是项目成员
            user_dict = {str(request.tracker.project.creator_id): request.tracker.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)  # 获取当前项目所有的成员
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({"status": False, "error": "数据错误或用户不存在"})
                username_list.append(username)
            # 更新数据库
            issue_obj.attention.set(value)
            issue_obj.save()
            change_msg = "{}更新为{}".format(field_obj.verbose_name, ",".join(username_list))
        return JsonResponse({"status": True, "data": create_reply_msg(change_msg)})

    return JsonResponse({"status": False, "error": "数据错误"})
