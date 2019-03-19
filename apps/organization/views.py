from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django.template.loader import render_to_string
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course
from operation.models import UserFavorite
from organization.forms import UserAskForm
from .models import CourseOrg, CityDict, Teacher


class OrgView(View):
    """机构列表"""
    def get(self, request):
        # 查找所有的机构
        all_orgs = CourseOrg.objects.all()

        # 热门机构,如果不加负号会是有小到大。
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords)
                | Q(desc__icontains=search_keywords)
                | Q(address__icontains=search_keywords)
            )
        # 地区
        all_city = CityDict.objects.all()  # 前端要用
        city_id = request.GET.get('city', '')
        if city_id:
            # 地区筛选
            all_orgs = all_orgs.filter(city_id=city_id)

        # 类别
        category = request.GET.get('ct', '')
        if category:
            # 类别筛选
            all_orgs = all_orgs.filter(category=category)

        # 进行排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':  # 学习人数
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':  # 课程数
                all_orgs = all_orgs.order_by('-course_nums')

        # 机构数量
        org_nums = all_orgs.count()
        page = request.GET.get('page', 1)
        # 分页
        p = Paginator(all_orgs, 4)
        try:
            orgs = p.page(page)
        except (PageNotAnInteger, EmptyPage):
            orgs = p.page(1)

        context = {
            'all_orgs': orgs,
            'all_city': all_city,
            'org_nums': org_nums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
            'search_keywords': search_keywords,
        }
        return render(request, 'org-list.html', context=context)


class AddUserAskView(View):
    """用户添加咨询"""
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            userask_form.save(commit=True)  # 保存
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail', 'msg': '您的字段有错误,请检查'})


class OrgHomeView(View):
    """机构首页"""
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = 'home'
        try:
            course_org = CourseOrg.objects.get(id=org_id)
        except CourseOrg.DoesNotExist:
            return render(request, '404.html')
        course_org.click_nums += 1
        course_org.save()
        # 是否收藏，机构
        has_fav = False
        if request.user.is_authenticated:  # 必须登录
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        # 检索机构下的课程和讲师
        all_courses = course_org.course_set.all()[:4]
        all_teacher = course_org.teacher_set.all()[:2]

        context = {
            'all_courses': all_courses,
            'all_teacher': all_teacher,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        }
        return render(request, 'org-detail-homepage.html', context=context)


class OrgCourseView(View):
    """机构课程列表页"""
    def get(self, request, org_id):
        # 向前端传值，表明现在在course页
        current_page = 'course'
        course_org = CourseOrg.objects.get(id= int(org_id))
        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外键引用
        all_courses = course_org.course_set.all()
        has_fav = False  # 机构收藏判断
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        context = {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-course.html', context=context)


class OrgDescView(View):
    """机构描述详情页"""
    def get(self, request, org_id):
        # 向前端传值，表明现在desc页
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id= int(org_id))
        has_fav = False   # 机构收藏判断
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        context = {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-desc.html', context=context)


class OrgTeacherView(View):
    """机构讲师列表页"""
    def get(self, request, org_id):
        # 向前端传值，表明现在在teacher页
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()
        has_fav = False  # 机构收藏判断
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        context = {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        }
        return render(request, 'org-detail-teachers.html', context=context)


class AddFavView(View):
    """用户收藏与取消收藏功能"""
    def post(self, request):
        id = request.POST.get('fav_id', None)
        type = request.POST.get('fav_type', None)
        try:
            int(id)
            int(type)
        except ValueError:
            return render(request, '500.html')
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'msg': '用户未登录'})

        # 查询收藏是否存在，（收藏，取消收藏依据）
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
        if exist_records:
            # 记录存在，取消收藏
            exist_records.delete()
            if int(type) == 1:
                course = Course.objects.get(id=id)
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = CourseOrg.objects.get(id=id)
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = Teacher.objects.get(id=id)
                teacher.fav_nums -=1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return JsonResponse({'status': 'success', 'msg': '收藏'})
        else:  # 添加收藏
            user_fav = UserFavorite()
            # 过滤掉未取到fav_id type的默认情况
            if type and id:
                user_fav.fav_id = id
                user_fav.fav_type = type
                user_fav.user = request.user
                user_fav.save()
                if int(type) == 1:
                    course = Course.objects.get(id=id)
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=id)
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=id)
                    teacher.fav_nums += 1
                    teacher.save()
                return JsonResponse({'status': 'success', 'msg': '已收藏'})
            else:
                return JsonResponse("{'status': 'fail', 'msg': '收藏出错'}")


class TeacherListView(View):
    """讲师列表"""
    def get(self, request):
        all_teacher = Teacher.objects.all()
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teacher = all_teacher.order_by('-click_nums')
        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teacher = all_teacher.filter(
                Q(name__icontains=search_keywords)
                | Q(work_company__icontains=search_keywords)
            )

        # 排行榜讲师
        rank_teacher = Teacher.objects.all().order_by('-fav_nums')[:5]
        # 数量统计
        teacher_nums = all_teacher.count()
        page = request.GET.get('page', 1)
        # 分页
        p = Paginator(all_teacher, 4)
        try:
            teachers = p.page(page)
        except (PageNotAnInteger, EmptyPage):
            teachers = p.page(1)

        context = {
            'all_teacher': teachers,
            'teacher_nums': teacher_nums,
            'sort': sort,
            'rank_teachers': rank_teacher,
            'search_keywords': search_keywords,
        }
        return render(request, 'teachers-list.html', context=context)


class TeacherDetailView(View):
    """教师详情"""
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            # return render(request, '404html')
            return HttpResponse(render_to_string('404.html'), content_type='text/html')
        teacher.click_nums += 1
        teacher.save()

        all_course = teacher.course_set.all()
        # 排行榜讲师
        rank_teacher = Teacher.objects.order_by('-fav_nums')[:5]

        has_fav_teacher = False  # 是否收藏讲师
        has_fav_org = False  # 是否收藏机构
        if request.user.is_authenticated:  # 防止未登陆时，request.user报错
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher_id):
                has_fav_teacher = True
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_fav_org = True

        context = {
            'teacher': teacher,
            'all_course': all_course,
            'rank_teacher': rank_teacher,
            'has_fav_teacher': has_fav_teacher,
            'has_fav_org': has_fav_org,
        }
        return render(request, 'teacher-detail.html', context=context)
