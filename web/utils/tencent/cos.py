#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# filename: cos.py
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = 'ap-beijing'  # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
# COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Scheme=scheme)
client = CosS3Client(config)


def create_bucket(bucket):
    """创建桶"""
    client.create_bucket(
        Bucket=bucket + "-" + settings.TENCENT_APP_ID,
        ACL="public-read"  # private  /  public-read / public-read-write
    )


def upload_file(bucket, file_obj, file_name):
    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_obj,
        file_name=file_name,
    )
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, file_name)
