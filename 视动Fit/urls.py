from django.contrib import admin
from django.urls import path, include
from user.views import register, custom_login, home, personal, exercise, run_python, address, record, \
    get_recent_exercises  # 导入视图函数
from django.conf import settings
from django.conf.urls.static import static
from 视动Fit import routing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # 包含默认的用户认证 URL
    path('register/', register, name='register'),  # 注册页面的URL路由
    path('login/', custom_login, name='login'),  # 登录页面的URL路由
    path('', home, name='home'),  # 主页的URL路由
    path('personal/', personal, name='personal'),
    path('exercise/', exercise, name='exercise'),
    path('exercise/run_python/', run_python, name='run_python'),
    path('personal/address/', address, name='address'),
    path('personal/exer/',get_recent_exercises,name='exer'),
    path('exercise/record/',record,name='record'),
    path('exercise/run_python/',run_python,name='run_python'),
    path('ws/', include(routing.websocket_urlpatterns)),
]

AUTH_USER_MODEL = 'user.User'
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
