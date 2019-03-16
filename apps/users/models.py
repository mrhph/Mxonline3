from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    # 定义性别选择规则
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女')
    )
    nick_name = models.CharField('昵称', max_length=50, blank=True, default='')
    birthday = models.DateField('生日', null=True, blank=True)
    gender = models.CharField('性别', max_length=6, choices=GENDER_CHOICES, default='female')
    address = models.CharField('地址', max_length=100, blank=True, default='')
    mobile = models.CharField('电话', max_length=11, null=True, blank=True)
    image = models.ImageField('头像', upload_to='image/%Y/%m', blank=True, default='image/default.png', max_length=100)

    class Meta:
        db_table = 'user'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    # 获取用户未读消息的数量
    def unread_nums(self):
        from operation.models import UserMessage
        return UserMessage.objects.filter(has_read=False, user=self.id).count()


class EmailVerifyRecord(models.Model):
    """邮箱验证码"""
    SEND_CHOICES = (
        ('register', '注册'),
        ('forget', '找回密码'),
        ('update_email', '修改邮箱'),
    )
    code = models.CharField('验证码', max_length=20)
    email = models.EmailField('邮箱', max_length=50)
    send_type = models.CharField('验证码类型', choices=SEND_CHOICES, max_length=20)
    # 这里的now去掉(),不去掉会根据编译时间。而不是根据实例化时间。
    send_time = models.DateTimeField('发送时间', default=datetime.now)

    class Meta:
        db_table = 'email_verify_record'
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)


class Banner(models.Model):
    """首页轮播图"""
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('轮播图', upload_to='banner/%Y/%m', max_length=100)
    url = models.URLField('访问地址', max_length=200)
    index = models.IntegerField('顺序', default=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'banner'
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}(位于第{1}位)'.format(self.title, self.index)