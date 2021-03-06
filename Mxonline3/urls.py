"""
Mxonline3 URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
# 导入xadmin，替换admin
from django.views.static import serve

import xadmin
from django.conf import settings
from django.conf.urls.static import static

from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView,\
    ResetView, ModifyPwdView, LogoutView, IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),  # x_admin
    path('captcha/', include('captcha.urls')),  # 验证码
    path('ueditor/', include('DjangoUeditor.urls')),  # 富文本

    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # 注册
    path('register/', RegisterView.as_view(), name='register'),
    # 激活用户
    re_path(r'active/(?P<active_code>.*)/', ActiveUserView.as_view(), name='user_active'),
    # 忘记密码
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    # 重置密码url：用来接收来自邮箱的重置链接
    re_path(r'reset/(?P<active_code>.*)/', ResetView.as_view(), name='reset_pwd'),
    # 修改密码, 只接收post请求
    path('modify_pwd/', ModifyPwdView.as_view(), name='modify_pwd'),

    # organization app, teacher
    path('org/', include('organization.urls', namespace='org')),
    # course
    path('course/', include('courses.urls', namespace='course')),
    # user
    path('users/', include('users.urls', namespace='users')),

]

# 处理图片显示的url,使用Django自带serve,传入参数路径
# 开发阶段配置配置上传文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)