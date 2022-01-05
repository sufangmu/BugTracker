#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import hashlib
from django.conf import settings


def md5(value):
    md5_obj = hashlib.md5(settings.SECRET_KEY.encode("utf-8"))
    md5_obj.update(value.encode("utf-8"))
    return md5_obj.hexdigest()
