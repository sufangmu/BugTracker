#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from django.urls import path, re_path, include
from web.views import account
from web.views import project
from web.views import manage
from web.views import wiki

urlpatterns = [
    path('register/', account.register, name='register'),
    path('send_sms/', account.send_sms, name='send_sms'),
    path('login/', account.login, name='login'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('image/code/', account.image_code, name='image_code'),
    path('', account.index, name='index'),
    path('logout/', account.logout, name='logout'),

    path('project/list', project.project_list, name='project_list'),
    re_path(r'project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/', project.project_star, name='project_star'),
    re_path(r'project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/', project.project_unstar,
            name='project_unstar'),
    # 项目管理
    re_path(r'manage/(?P<project_id>\d+)/', include([
        path('dashboard/', manage.dashboard, name='dashboard'),
        path('issue/', manage.issue, name='issue'),
        path('statistics/', manage.statistics, name='statistics'),
        path('file/', manage.file, name='file'),
        path('wiki/', wiki.wiki, name='wiki'),
        path('wiki/add/', wiki.wiki_add, name='wiki_add'),
        re_path(r'wiki/delete/(?P<wiki_id>\d+)/', wiki.wiki_delete, name='wiki_delete'),

        path('wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),
        path('setting/', manage.setting, name='setting'),
    ], None)),

]
