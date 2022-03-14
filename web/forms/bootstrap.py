#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

class BootStrapForm:
    bootstrap_class_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # 设置某些字段不添加样式
            if name in self.bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = '{} form-control'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)
