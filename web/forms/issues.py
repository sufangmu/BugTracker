from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models


class IssuesForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ["project", "creator", "create_datetime", "latest_update_datetime"]
