from courses.views import CourseListView, CourseDetailView, CourseInfoView,\
    CommentsView, AddCommentsView, VideoPlayView
from django.urls import path, re_path

app_name = 'courses'
urlpatterns = [
    # 课程列表url
    path('list/', CourseListView.as_view(), name='list'),
    # 课程详情
    re_path('detail/(?P<course_id>\d+)/', CourseDetailView.as_view(), name='course_detail'),
    # 课程章节列表
    re_path('info/(?P<course_id>\d+)/', CourseInfoView.as_view(), name='course_info'),
    # 课程评论
    re_path('comments/(?P<course_id>\d+)/', CommentsView.as_view(), name='course_comments'),
    # 添加课程评论
    path('add_comment/', AddCommentsView.as_view(), name='add_comment'),
    # 课程视频播放页
    re_path('video/(?P<video_id>\d+)/', VideoPlayView.as_view(), name='video_play'),
]
