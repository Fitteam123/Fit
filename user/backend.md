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
## crsf处理
### fetch
- html:<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
- javascript:fetch('address/', {
				method: 'POST',
							headers: {
                                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
								'Content-Type': 'application/json',
							},
							body: JSON.stringify({ address: address }),
						})
### form
- <form action="{% url '' %}" method="post">
**{% csrf_token %}**
<!-- 表单字段 -->
<button type="submit">提交</button>
</form>
