import os
from celery import Celery

# 设置默认的Django配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user.settings')

# 创建Celery应用程序
app = Celery('视动Fit')

# 使用Django配置中的配置来配置Celery应用程序
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动发现并注册任务
app.autodiscover_tasks()

