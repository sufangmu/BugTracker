#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from django.urls import path, re_path, include
from web.views import account
from web.views import project
from web.views import wiki
from web.views import file
from web.views import setting
from web.views import issues
from web.views import dashboard
from web.views import statistics

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
        path('dashboard/', dashboard.dashboard, name='dashboard'),
        path('dashboard/issues/chart', dashboard.issues_chart, name='issues_chart'),
        path('statistics/', statistics.statistics, name='statistics'),
        path('file/', file.file, name='file'),
        path('file/delete/', file.file_delete, name='file_delete'),
        path('file/post/', file.file_post, name='file_post'),
        re_path(r'file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),
        path('cos/credential/', file.cos_credential, name='cos_credential'),

        path('wiki/', wiki.wiki, name='wiki'),
        path('wiki/add/', wiki.wiki_add, name='wiki_add'),
        re_path(r'wiki/delete/(?P<wiki_id>\d+)/', wiki.wiki_delete, name='wiki_delete'),
        re_path(r'wiki/edit/(?P<wiki_id>\d+)/', wiki.wiki_edit, name='wiki_edit'),
        re_path(r'wiki/upload/', wiki.wiki_upload, name='wiki_upload'),
        path('wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),

        path('setting/', setting.setting, name='setting'),
        path('setting/delete/', setting.delete, name='setting_delete'),

        path('issue/', issues.issue, name='issue'),
        re_path(r'issue/detail/(?P<issue_id>\d+)/', issues.issue_detail, name='issue_detail'),
        re_path(r'issue/replies/(?P<issue_id>\d+)/', issues.issue_replies, name='issue_replies'),
        re_path(r'issue/change/(?P<issue_id>\d+)/', issues.issue_change, name='issue_change'),
        path('issue/invite/url/', issues.invite_url, name='invite_url'),
    ], None)),
    re_path(r'invite/join/(?P<code>\w+)', issues.invite_join, name='invite_join'),
]
