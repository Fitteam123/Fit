# url编写
- path('personal/' 此处为前端地址, personal此处为视图函数名, name='personal'此处为前端post名),
# 测试命令
- python manage.py test
# 自动生成模型
- python manage.py inspectdb 
# 数据库迁移命令
- python manage.py makemigrations
- python manage.py migrate
# 启动服务器
- daphne -p 8000 视动Fit.asgi:application
