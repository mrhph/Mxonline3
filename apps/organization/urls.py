from organization.views import OrgView, AddUserAskView, OrgHomeView, OrgCourseView, \
    OrgDescView, OrgTeacherView, AddFavView, TeacherListView, TeacherDetailView

from django.urls import path, re_path

app_name = 'organization'
urlpatterns = [
    # 课程机构列表
    path('list/', OrgView.as_view(), name='org_list'),
    # 机构首页
    re_path('home/(?P<org_id>\d+)/', OrgHomeView.as_view(), name='org_home'),
    # 访问课程
    re_path('course/(?P<org_id>\d+)/', OrgCourseView.as_view(), name='org_course'),
    # 机构描述
    re_path('desc/(?P<org_id>\d+)/', OrgDescView.as_view(), name='org_desc'),
    # 机构讲师
    re_path('org_teacher/(?P<org_id>\d+)/', OrgTeacherView.as_view(), name='org_teacher'),
    # 用户咨询，post，在机构列表页
    path('add_ask/', AddUserAskView.as_view(), name='add_ask'),
    # 机构收藏， post
    path('add_fav/', AddFavView.as_view(), name='add_fav'),

    # 讲师列表
    path('teacher/list/', TeacherListView.as_view(), name='teacher_list'),
    # 讲师详情
    re_path('teacher/detail/(?P<teacher_id>\d+)/', TeacherDetailView.as_view(), name='teacher_detail'),
]