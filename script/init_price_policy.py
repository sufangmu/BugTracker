#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: init_price_policy.py

import base
from web import models


def run():
    exist = models.PricePolicy.objects.filter(category=1, title="个人免费版").exists()
    if not exist:
        models.PricePolicy.objects.create(
            category=1,
            title="个人免费版",
            price=0,
            project_num=3,
            project_member=3,
            project_space=128,
            per_file_size=5,
        )


if __name__ == '__main__':
    run()
