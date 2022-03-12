from django.db import models


class UserInfo(models.Model):
    """用户表"""
    username = models.CharField(verbose_name='用户名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=11)
    password = models.CharField(verbose_name='密码', max_length=32)


class PricePolicy(models.Model):
    """价格策略"""
    category_choices = (
        (1, "免费版"),
        (2, "收费版"),
        (3, "其他"),
    )

    category = models.SmallIntegerField(verbose_name="收费类型", choices=category_choices, default=1)
    title = models.CharField(verbose_name="标题", max_length=32)
    price = models.PositiveIntegerField(verbose_name="价格")
    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_member = models.PositiveIntegerField(verbose_name="项目成员数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间(G)")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小(M)")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Transaction(models.Model):
    """交易记录"""
    status_choices = (
        (1, "未支付"),
        (2, "已支付"),
    )

    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.DO_NOTHING)
    price_policy = models.ForeignKey(verbose_name="价格策略", to="PricePolicy", on_delete=models.DO_NOTHING)
    count = models.IntegerField(verbose_name="数量(年)", help_text="0表示无限期")
    price = models.IntegerField(verbose_name="实际支付价格")
    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Project(models.Model):
    """项目表"""
    color_choices = (
        (1, "#56b8eb"),
        (2, "#f28033"),
        (3, "#ebc656"),
        (4, "#a2d148"),
        (5, "#20bfa4"),
        (6, "#7461c2"),
        (7, "#20bfa3"),
    )

    name = models.CharField(verbose_name="项目名称", max_length=32)
    color = models.SmallIntegerField(verbose_name="颜色", choices=color_choices, default=1)
    desc = models.CharField(verbose_name="描述", max_length=255, null=True, blank=True)
    use_space = models.IntegerField(verbose_name="已使用空间", default=0)
    star = models.BooleanField(verbose_name="星标", default=False)
    join_count = models.SmallIntegerField(verbose_name="参与人数", default=1)
    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo", on_delete=models.DO_NOTHING)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    bucket = models.CharField(verbose_name="COS桶", max_length=128)
    # 便于查询，但无法完成增加，删除，修改操作，此外through_fields字段顺序要与ProjectUser保持一致
    # project_user = models.ManyToManyField(to="UserInfo", through="ProjectUser", through_fields=("project", "user"))


class ProjectUser(models.Model):
    """项目参与者"""
    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.DO_NOTHING)
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.DO_NOTHING)
    star = models.BooleanField(verbose_name="星标", default=False)
    create_datetime = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)


class Wiki(models.Model):
    """Wiki"""
    title = models.CharField(verbose_name="标题", max_length=255, default='')
    content = models.TextField(verbose_name="内容")
    project = models.ForeignKey(to="Project", verbose_name="项目", on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(verbose_name="父文档", to="self", null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="children")

    depth = models.IntegerField(verbose_name="深度", default=1)

    def __str__(self):
        return self.title


class FileRepository(models.Model):
    """文件库"""
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    file_type_choices = (
        (1, "文件"),
        (2, "目录"),
    )
    file_type = models.SmallIntegerField(verbose_name="类型", choices=file_type_choices)
    name = models.CharField(verbose_name="名称", max_length=128, help_text="文件/目录名")
    key = models.CharField(verbose_name="存在在COS中KEY", max_length=128, null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name="文件大小", null=True, blank=True, help_text="字节")
    file_path = models.CharField(verbose_name="文件路径", max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name="父目录", to="self", related_name="children", blank=True, null=True,
                               on_delete=models.CASCADE)
    update_user = models.ForeignKey(verbose_name="最近更新者", to="UserInfo", on_delete=models.SET_NULL, null=True)
    update_datetime = models.DateTimeField(verbose_name="更新时间", auto_now=True)
