from django import forms
from django.core.exceptions import ValidationError

from web.forms.bootstrap import BootStrapForm
from web import models


class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ["name", ]

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        name = self.cleaned_data["name"]
        # 判断当前目录下是否存在同名目录
        queryset = models.FileRepository.objects.filter(file_type=2, name=name, project=self.request.tracker.project)

        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError("文件夹已存在")
        return name