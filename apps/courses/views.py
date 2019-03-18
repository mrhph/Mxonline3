from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse


class CourseListView(View):
    """课程列表"""
    def get(self, request):
        all_course = Course.objects.all()
        # 热门课程推荐
        hot_courses = Course.objects.all().order_by('-students')[:3]
        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            all_course = all_course.filter(
                Q(name__icontains=search_keywords)
                | Q(desc__icontains=search_keywords)
                | Q(detail__icontains=search_keywords)
            )
        sort = request.GET.get('sort', '')  # 排序方式
        if sort:
            if sort == 'students':
                all_course = all_course.order_by('-students')
            elif sort == 'hot':
                all_course = all_course.order_by('-click_nums')

        page = request.GET.get('page', 1)
        p = Paginator(all_course, 6, request=request)
        try:
            courses = p.page(page)
        except (PageNotAnInteger, EmptyPage):
            courses = p.page(1)
        context = {
            'all_course': courses,
            'sort': sort,
            'hot_courses': hot_courses,
            'search_keywords': search_keywords
        }
        return render(request, 'course-list.html', context=context)


class CourseDetailView(View):
    """课程详情"""
    def get(self, request, course_id):
        # 此处的id为表默认为我们添加的值。
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return render(request, '404.html')
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 是否收藏课程
        has_fav_course = False
        has_fav_org = False

        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        # 取出标签找到标签相同的course
        tag = course.tag
        if tag:
            # exclude()返回不满足给定的查找参数的对象的QuerySet
            relate_courses = Course.objects.filter(tag=tag).exclude(id=course.id)[0:1]
        else:
            relate_courses = Course.objects.exclude(id=course.id)[0:1]

        context = {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        }
        return render(request, 'course-detail.html', context=context)


class CourseInfoView(LoginRequiredMixin, View):
    """课程章节列表"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return render(request, '404.html')

        # 查询用户是否开始学习了该课，如果还未学习则，加入用户课程表
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            UserCourse.objects.create(user=request.user, course=course)
            course.students += 1
            course.save()

        # 查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        # 取出学了这门课的所有学生
        user_courses = UserCourse.objects.filter(course=course)
        # 取出user_id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 取出这些学生所学的所有课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        # 获取学过该课程用户学过的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums').exclude(id=course.id)[:4]

        context = {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        }
        return render(request, 'course-video.html', context=context)


class CommentsView(LoginRequiredMixin, View):
    """课程评论"""
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            from django.template.loader import render_to_string
            return HttpResponse(render_to_string('404.html', content_type='text/html'))

        # 课程资源，同课程章节列表
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).order_by('-add_time')
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course_id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums').exclude(id=course.id)[:4]

        context = {
            'course': course,
            'all_resources': all_resources,
            'all_comments': all_comments,
            'relate_courses': relate_courses,
        }
        return render(request, 'course-comment.html', context=context)


class AddCommentsView(View):
    """ajax方式添加评论"""
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return JsonResponse({'status': 'fail', 'msg': '用户未登录'})
        course_id = request.POST.get('course_id', None)
        comments = request.POST.get('comments', None)
        if course_id and comments:
            try:
                course = Course.objects.get(id=course_id)
            except (Course.DoesNotExist, Course.MultipleObjectsReturned):
                return JsonResponse({'status': 'fail', 'msg': 'err'})
            # 存入对象
            course_comments = CourseComments()
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return JsonResponse({'status': 'success', 'msg': '评论成功'})
        else:
            return JsonResponse({'status': 'fail', 'msg': '评论失败'})


class VideoPlayView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return render(request, '404.html')

        course = video.lesson.course
        # 查询用户是否开始学习了该课，如果还未学习则加入用户课程表
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 查询课程资源，同课程章节列表
        all_resources = CourseResource.objects.filter(course=course)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course_id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums').exclude(id=course.id)[:4]

        context = {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        }
        return render(request, 'course-play.html', context=context)