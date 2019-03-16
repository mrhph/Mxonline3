import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from utils.email_send import send_email
from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ActiveForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm


class RegisterView(View):
    """注册"""
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            # 用户查重
            if UserProfile.objects.filter(email=user_name):
                context = {'register_form': register_form, 'msg': '用户已存在'}
                return render(request, 'register.html', context=context)

            pass_word = request.POST.get('password', '')
            # 实例化一个user_profile对象，将前台值存入
            user_profile = UserProfile.objects.create(
                username=user_name,
                email=user_name,
                password=make_password(pass_word),
                is_active=False
            )
            # 写入欢迎注册消息
            user_message = UserMessage.objects.create(
                user=user_profile.id,
                message='欢迎注册慕课小站!! --系统自动消息',
            )

            # 发送注册激活邮件
            send_email(user_name, send_type='register')
            return render(request, 'login.html', {'msg': '邮件已发送，请去激活账户'})
        else:
            # 注册邮箱form验证失败
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    """激活用户"""
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        active_form = ActiveForm(request.GET)
        if all_record:
            record = all_record.first()  # 获取record
            email = record.email
            user = UserProfile.objects.get(email=email)
            user.is_active = True
            user.save()
            record.delete()
            # 激活成功跳转到登录页面
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'msg': '您的激活链接无效', 'active_form': active_form})


class CustomBackend(ModelBackend):
    """
    实现用户名邮箱均可登录,继承ModelBackend类，因为它有方法authenticate
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # Q为使用并集查询, 或者
            user = UserProfile.objects.get(
                Q(username=username) | Q(email=username)
            )
            if user.check_password(password):  # 检查密码，匹配返回True
                return user
        except UserProfile.DoesNotExist:
            return HttpResponse(render_to_string('404.html'), content_type='text/html')


class LoginView(View):
    """登录"""
    def get(self, request):
        redirect_url = request.GET.get('next', '')
        return render(request, 'login.html', {'redirect_url': redirect_url})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')

            # 成功返回user对象,失败返回null
            user = authenticate(username=user_name, password=pass_word)

            if user is not None:
                if user.is_active:  # 激活状态
                    login(request, user)  # 登录
                    redirect_url = request.POST.get('next', '')
                    if redirect_url:
                        return redirect(redirect_url)
                    return redirect(reverse('index'))
                else:  # 未激活
                    return render(request, 'login.html', {'msg': '用户名未激活! 请前往邮箱进行激活'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误!'})
        # 验证不成功跳回登录页面
        else:
            return render(request, 'login.html', {'login_form': login_form})


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        # django自带的logout
        logout(request)
        return redirect(reverse('index'))


# 登录， 抛弃方法型实现，改为类实现
def user_login(request):
    if request.method == 'POST':
        user_name = request.POST.get('username', '')
        pass_word = request.POST.get('password', '')
        user = authenticate(username=user_name, password=pass_word)

        if user is not None:
            login(request, user)
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'msg': '用户名或密码错误! '})
    elif request.method == 'GET':
        return render(request, 'login.html')


class ForgetPwdView(View):
    """忘记密码"""
    def get(self, request):
        # 给忘记密码页面加上验证码
        active_form = ActiveForm()
        return render(request, 'forgetpwd.html', {'active_form': active_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            # 发送找回密码邮件
            send_email(email, send_type='forget')
            # 发送完毕返回登录页面并提示发送邮件成功。
            return render(request, 'login.html', {'msg': '重置密码邮件已发送,请注意查收'})
        else:
            return render(request, 'forgetpwd.html', {'forget_from': forget_form})


class ResetView(View):
    """重置密码"""
    def get(self, request, active_code):
        active_form = ActiveForm(request.GET)
        try:
            record = EmailVerifyRecord.objects.get(code=active_code)
            email = record.email  # 直接传email有安全风险
            return render(request, 'password_reset.html', {'active_code': active_code})
        except EmailVerifyRecord.DoesNotExist:  # 查询不到此验证码
            context = {'msg': '您的重置密码链接无效,请重新请求', 'active_form': active_form}
            return render(request, 'forgetpwd.html', context=context)


class ModifyPwdView(View):
    """修改密码"""
    def post(self, request):
        modiypwd_form = ModifyPwdForm(request.POST)
        if modiypwd_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            active_code = request.POST.get('active_code', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'msg': '密码不一致', 'active_code': active_code})
            # 拿到对应的邮箱
            try:
                record = EmailVerifyRecord.objects.get(code=active_code)
            except EmailVerifyRecord.DoesNotExist:  # 数据库无此验证码
                return JsonResponse({'status': 'err'})

            email = record.email
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)  # 加密存储
            user.save()
            record.delete()  # 修改成功删除验证码，防止验证码泄露，减小数据容量，
            return render(request, 'login.html', {'msg': '密码修改成功，请登录'})
        # 验证失败
        else:
            active_code = request.POST.get('active_code', '')
            context = {'active_code': active_code, 'modiypwd_form': modiypwd_form}
            return render(request, 'password_reset.html', context=context)


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, 'usercenter-info.html')

    def post(self, request):
        # 指明instance，代表修改module不是新增
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({'status': 'success'})
        else:
            # 通过json的dumps方法把字典转换为json字符串
            return JsonResponse(json.dumps(user_info_form.errors))


class UploadImageView(LoginRequiredMixin, View):
    """修改头像"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        # 用户上传的文件就已经保存到image_form
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail'})


class UpdatePwdView(LoginRequiredMixin, View):
    """个人中心修改用户密码"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return JsonResponse({'status': 'fail', 'msg': '密码不一致'})
            user = request.user
            user.password = make_password(pwd2)
            user.save()  # 保存
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse(json.dumps(modify_form.errors),)


class SendEmailCodeView(LoginRequiredMixin, View):
    """个人中心发送邮箱验证码"""
    def get(self, request):
        email = request.GET.get('email', '')
        # 不能是已注册的邮箱
        if UserProfile.objects.filter(email=email):
            return JsonResponse({'email': '邮箱已经存在'})
        send_email(email, send_type='update_email')
        return JsonResponse({'status': 'success'})


class UpdateEmailView(LoginRequiredMixin, View):
    """修改邮箱"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        try:
            record = EmailVerifyRecord.objects.get(
                email=email, code=code, send_type='update_email')  # 查询验证码是否存在
        except EmailVerifyRecord.DoesNotExist:
            return JsonResponse({'email': '验证码无效'})
        # 验证码存在，修改邮箱
        user = request.user
        user.email = email
        user.save()
        record.delete()
        return JsonResponse({'status': 'success'})


# 个人中心页我的课程
class MyCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {'user_courses': user_courses})


# 我收藏的机构
class MyFavOrgView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {'org_list': org_list,})


# 我收藏的授课讲师
class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        teacher_list = []  # 存放教师
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {'teacher_list': teacher_list})


# 我收藏的课程
class MyFavCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {'course_list': course_list,})


# 我的消息
class MyMessageView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        all_message = UserMessage.objects.filter(user= request.user.id)

        # 用户进入个人中心消息页面，清空未读消息记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()
        # 对课程机构进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从allorg中取五个出来，每页显示5个
        p = Paginator(all_message, 4)
        messages = p.page(page)
        return render(request, 'usercenter-message.html', {'messages': messages})


# 首页view
class IndexView(View):
    def get(self,request):
        # 取出轮播图
        all_banner = Banner.objects.all().order_by('index')[:5]
        # 正常位课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播图课程取三个
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        context = {
            'all_banner': all_banner,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        }
        return render(request, 'index.html', context=context)
