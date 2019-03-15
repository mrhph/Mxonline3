from datetime import datetime

from django.db import models


# 城市字典
class CityDict(models.Model):
    name = models.CharField('城市', max_length=20)
    # 城市描述：备用不一定展示出来
    desc = models.CharField('描述', max_length=200)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'city_dict'
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 课程机构
class CourseOrg(models.Model):
    ORG_CHOICES = (
        ('pxjg', '培训机构'),
        ('gx', '高校'),
        ('gr', '个人'),
    )
    name = models.CharField('机构名称', max_length=50)
    # 机构描述，后面会替换为富文本展示
    desc = models.TextField('机构描述')
    # 机构类别
    category = models.CharField('机构类别', max_length=20, choices=ORG_CHOICES, default='pxjg')
    tag = models.CharField('机构标签', max_length=10, default='国内名校')
    click_nums = models.IntegerField('点击数', default=0)
    fav_nums = models.IntegerField('收藏数', default=0)
    image = models.ImageField('Logo', upload_to='org/%Y/%m', max_length=100)
    address = models.CharField('机构地址', max_length=150)
    # 一个城市可以有很多课程机构，通过将city设置外键，变成课程机构的一个字段
    city = models.ForeignKey(CityDict, on_delete=models.CASCADE, verbose_name='所在城市')
    # 当学生点击学习课程，找到所属机构，学习人数加1
    students = models.IntegerField('学习人数', default=0)
    # 当发布课程就加1
    course_nums = models.IntegerField('课程数', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'course_org'
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '课程机构: {0}'.format(self.name)


# 讲师
class Teacher(models.Model):
    # 一个机构会有很多老师，所以我们在讲师表添加外键并把课程机构名称保存下来
    # 可以使我们通过讲师找到对应的机构
    org = models.ForeignKey(CourseOrg,  on_delete=models.CASCADE, verbose_name='所属机构')
    name = models.CharField('教师名称', max_length=50)
    work_years = models.IntegerField('工作年限', default=0)
    work_company = models.CharField('就职公司', max_length=50)
    work_position = models.CharField('公司职位', max_length=50)
    age = models.IntegerField('年龄', default=18)
    points = models.CharField('教学特点', max_length=50)
    click_nums = models.IntegerField('点击数', default=0)
    fav_nums = models.IntegerField('收藏数', default=0)
    image = models.ImageField('头像', max_length=100, upload_to='teacher/%Y/%m', default='')
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        db_table = 'teacher'
        verbose_name = '教师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '[{0}]的教师: {1}'.format(self.org, self.name)
