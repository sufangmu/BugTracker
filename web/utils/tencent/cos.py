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
        Bucket=bucket,
        ACL="public-read"  # private  /  public-read / public-read-write
    )
    # 解决跨域问题
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_file(bucket, file_obj, file_name):
    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_obj,
        Key=file_name,
    )
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, file_name)


def delete_file(bucket, file_name):
    client.delete_object(
        Bucket=bucket,
        Key=file_name,
    )


def delete_files(bucket, file_list):
    objects = {
        "Quiet": "true",
        "Object": file_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )


def check_file(bucket, key):
    response = client.head_object(
        Bucket=bucket,
        Key=key,
    )
    return response


def credential(bucket):
    """ 获取cos上传临时凭证 """

    from sts.sts import Sts

    _config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 500,
        # 固定密钥 id
        'secret_id': settings.TENCENT_SECRET_ID,
        # 固定密钥 key
        'secret_key': settings.TENCENT_SECRET_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }

    sts = Sts(_config)
    result_dict = sts.get_credential()
    return result_dict
