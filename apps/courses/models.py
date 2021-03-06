from datetime import datetime
from django.db import models
from django.utils import timezone

from DjangoUeditor.models import UEditorField
from organization.models import CourseOrg, Teacher


class Course(models.Model):
    """课程信息表"""
    DEGREE_CHOICES = (
        ('cj', '初级'),
        ('zj', '中级'),
        ('gj', '高级')
    )
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name='所属机构', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师', null=True, blank=True)
    name = models.CharField('课程名', max_length=50)
    desc = models.CharField('课程描述', max_length=300)
    # 修改imagepath,不能传y m 进来，不能加斜杠是一个相对路径，相对于setting中配置的mediaroot
    detail = UEditorField('课程详情', width=600, height=300, imagePath='courses/ueditor/', filePath='courses/ueditor/', default='')
    is_banner = models.BooleanField('是否轮播', default=False)
    degree = models.CharField('难度', choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField('学习时长(分钟数)', default=0)
    students = models.IntegerField('学习人数', default=0)
    fav_nums = models.IntegerField('收藏人数', default=0)
    you_need_know = models.CharField('课程须知', max_length=300, default='一颗勤学的心是本课程必要前提')
    teacher_tell = models.CharField('老师告诉你', max_length=300, default='什么都可以学到,按时交作业,不然叫家长')
    image = models.ImageField('封面图', upload_to='courses/%Y/%m',  max_length=100)
    click_nums = models.IntegerField('点击数', default=0)
    category = models.CharField('课程类别', max_length=20, default='后端开发')
    tag = models.CharField('课程标签', max_length=15, default='')
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'course'
        verbose_name = '课程'
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.name


class Lesson(models.Model):
    """章节"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    name = models.CharField('章节名', max_length=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'lesson'
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course, self.name)


class Video(models.Model):
    """每章视频"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='章节')
    url = models.CharField('访问地址', max_length=200, default='')
    name = models.CharField('视频名', max_length=100)
    learn_times = models.IntegerField('学习时长(分钟数)', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'video'
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}的视频 >> {1}'.format(self.lesson, self.name)


class CourseResource(models.Model):
    """课程资源"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    name = models.CharField('名称', max_length=100)
    # FileField是一个字符串类型，要指定最大长度。
    download = models.FileField('资源文件', upload_to='course/resource/%Y/%m', max_length=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'course_resource'
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '《{0}》课程的资源: {1}'.format(self.course, self.name)
