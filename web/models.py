from django.db import models


class UserInfo(models.Model):
    """用户表"""
    username = models.CharField(verbose_name='用户名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=11)
    password = models.CharField(verbose_name='密码', max_length=32)

    def __str__(self):
        return self.username


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


class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.DO_NOTHING)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssueType', on_delete=models.DO_NOTHING)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.DO_NOTHING)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True,
                               on_delete=models.DO_NOTHING)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems',
                                on_delete=models.DO_NOTHING)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class Module(models.Model):
    """issue模块"""
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.DO_NOTHING)
    title = models.CharField(verbose_name="模块名称", max_length=32)

    def __str__(self):
        return self.title


class IssueType(models.Model):
    ISSUE_TYPE_INIT_LIST = ["任务", "功能", "Bug"]

    title = models.CharField(verbose_name="类型名称", max_length=32)
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title


class IssueReply(models.Model):
    """问题回复"""

    reply_type_choices = (
        (1, "修改记录"),
        (2, "回复"),
    )
    reply_type = models.IntegerField(verbose_name="类型", choices=reply_type_choices)
    issues = models.ForeignKey(verbose_name="问题", to="Issues", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="描述")
    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo", related_name="create_reploy", on_delete=models.DO_NOTHING)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    reply = models.ForeignKey(verbose_name="回复", to="self", null=True, blank=True, on_delete=models.CASCADE)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    used_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_invite', on_delete=models.CASCADE)
