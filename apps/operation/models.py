from datetime import datetime
from django.db import models

from users.models import UserProfile
from courses.models import Course


class UserAsk(models.Model):
    """用户咨询"""
    name = models.CharField('姓名', max_length=20)
    mobile = models.CharField('手机', max_length=11)
    course_name = models.CharField('课程名', max_length=50)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'user_ask'
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '用户: {0} 手机号: {1}'.format(self.name, self.mobile)


class CourseComments(models.Model):
    """用户对于课程评论"""
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    comments = models.CharField('评论', max_length=250)
    add_time = models.DateTimeField('评论时间', default=datetime.now)

    class Meta:
        db_table = 'course_comments'
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '用户({0})对于《{1}》 评论 :'.format(self.user, self.course)


class UserFavorite(models.Model):
    """用户对于课程,机构，讲师的收藏"""
    TYPE_CHOICES = (
        (1, '课程'),
        (2, '课程机构'),
        (3, '讲师')
    )

    user = models.ForeignKey(UserProfile,  verbose_name='用户', on_delete=models.CASCADE)
    # 保存收藏的id.
    fav_id = models.IntegerField(default=0)
    # 收藏的类型。
    fav_type = models.IntegerField('收藏类型', choices=TYPE_CHOICES, default=1)
    add_time = models.DateTimeField('评论时间', default=datetime.now)

    class Meta:
        db_table = 'user_favorite'
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '用户({0})收藏了{1} '.format(self.user, self.fav_type)


class UserMessage(models.Model):
    """用户消息"""
    # 为0发给所有用户，不为0发给用户的id
    user = models.IntegerField('接收用户', default=0)
    message = models.CharField('消息内容', max_length=500)
    has_read = models.BooleanField('是否已读', default=False)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'user_message'
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '用户({0})接收了{1} '.format(self.user, self.message)


class UserCourse(models.Model):
    """用户课程表"""
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'user_course'
        verbose_name = '用户课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '用户({0})学习了{1} '.format(self.user, self.course)
