from django import forms
from django.core.exceptions import ValidationError

from web.forms.bootstrap import BootStrapForm
from web import models
from web.utils.tencent import cos


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


class FileModelForm(BootStrapForm, forms.ModelForm):
    etag = forms.CharField(label="etag")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = models.FileRepository
        exclude = ["project", "file_type", "update_user", "update_datetime"]

    def clean_file_path(self):
        return "https://{}".format(self.cleaned_data["file_path"])

    def clean(self):
        """验证前端用户发送的请求数据是否正确"""
        etag = self.cleaned_data["etag"]
        key = self.cleaned_data["key"]
        size = self.cleaned_data["file_size"]

        if not key or not etag:
            return self.cleaned_data

        from qcloud_cos.cos_exception import CosServiceError
        # 向COS校验文件是否合法
        try:
            res = cos.check_file(self.request.tracker.project.bucket, key)
        except CosServiceError as exc:
            return self.add_error(key, "文件上传失败")
            return self.cleaned_data

        cos_etag = res.get("etag")
        if etag != cos_etag:
            return self.add_error("etag", "etag错误")

        cos_length = res.get("Content-Length")
        if int(cos_length) != size:
            self.add_error('size', "文件大小错误")

        return self.cleaned_data
