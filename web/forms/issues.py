from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models


class IssuesForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ["project", "creator", "create_datetime", "latest_update_datetime"]
        widgets = {
            "module": forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),
            "assign": forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(
                attrs={"class": "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),

        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        # 处理数据初始化
        # 获取当前项目的问题类型
        self.fields["issues_type"].choices = models.IssueType.objects.filter(
            project=self.request.tracker.project).values_list("id", "title")
        # 获取当前项目的模块
        module_list = [("", "没有选中任何项"), ]
        module_obj_list = models.Module.objects.filter(project=self.request.tracker.project).values_list("id", "title")
        module_list.extend(module_obj_list)
        self.fields["module"].choices = module_list

        # 指派和关注者
        # 找到当前项目的参与者和创建者
        total_user_list = [(self.request.tracker.project.creator_id, self.request.tracker.project.creator.username), ]
        project_user_list = models.ProjectUser.objects.filter(project=self.request.tracker.project).values_list(
            "user_id", "user__username")
        total_user_list.extend(project_user_list)
        self.fields["assign"].choices = total_user_list
        self.fields["attention"].choices = total_user_list

        # 当前项目创建的问题
        parent_subject_list = [("", "没有选中任何项"), ]

        parent_subject_obj_list = models.Issues.objects.filter(
            project=self.request.tracker.project).values_list("id", "subject")
        parent_subject_list.extend(parent_subject_obj_list)
        self.fields["parent"].choices = parent_subject_list
