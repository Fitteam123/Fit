from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import User, Exercise
from django.views.decorators.csrf import csrf_protect
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
def home(request):
    return render(request, 'home.html')

@login_required
def exercise(request):
    return render(request, 'exercise.html')

@login_required
def personal(request):
    return render(request, 'personal.html')


@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        login_user_id = request.POST.get('login_user_id')
        login_user_password = request.POST.get('login_user_password')
        # 使用Django默认的用户验证
        user = authenticate(request, username=login_user_id, password=login_user_password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'personal'})
        else:
            return JsonResponse({'success': False, 'message': '登录失败，账号或密码错误'})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        id = request.POST.get('user_id')
        password = request.POST.get('user_password')

        # 检查账号是否已存在
        if User.objects.filter(username=id).exists():
            return JsonResponse({'success': False, 'message': '该账号已存在，请选择另一个账号'})
        else:
            # 创建新的用户并保存
            new_user = User.objects.create_user(username=id, password=password)
            return JsonResponse({'success': True, 'message': '注册成功'})

    return JsonResponse({'success': False, 'message': '仅支持POST请求'})

from .tasks import run_python_script
def run_python(request):
    # 记录收到的请求
    # print("收到 POST 请求")#调试点
    if request.method == 'POST':
        # 触发异步任务
        # print("触发异步任务")#调试点
        run_python_script('test.py')
        return HttpResponse(status=200)  # 成功
    else:
        return HttpResponse(status=405)  # 方法不允许

@csrf_protect
def address(request):
    if request.method == 'POST':
        # print("收到address_post")
        # 解析请求体中的数据
        try:
            data = json.loads(request.body)
            user_address = data.get('address')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '请求数据解析失败'}, status=400)
        # 检查地址数据是否存在
        if not user_address:
            return JsonResponse({'success': False, 'message': '未提供地址信息'}, status=400)
        # 检查用户是否已认证
        # if not request.user.is_authenticated:
        #     return JsonResponse({'success': False, 'message': '用户未认证'}, status=401)
        # 保存地址信息到用户模型中
        user = request.user
        user.user_address = user_address
        user.save()
        # print("保存成功")
        return JsonResponse({'success': True, 'message': '地址保存成功！'})
    # 处理不支持的请求方法
    return JsonResponse({'success': False, 'message': '仅支持POST请求'}, status=405)

@csrf_exempt
def record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exercisetime = data.get('exercisetime')
            if exercisetime is None:
                return JsonResponse({'success': False, 'message': 'exercisetime is required'})
            user = request.user
            Exercise.objects.create(username=user, exercisetime=exercisetime, exercise_time=timezone.now())
            return HttpResponse(status=200)
        except json.JSONDecodeError:
            return HttpResponse(status=405)
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
@login_required
def get_recent_exercises(request):
    user = request.user
    recent_exercises = Exercise.objects.filter(username=user).order_by('-exercise_time')[:15]

    exercises_list = []
    for exer in recent_exercises:
        exercises_list.append({
            'exercise_time': exer.exercise_time,
            'exercisetime': exer.exercisetime
        })

    user_data = {
        'username': user.username
    }

    return JsonResponse({'success': True, 'name': user_data, 'exercises': exercises_list})
