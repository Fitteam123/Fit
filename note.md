# 版本信息
- python=3.7
- mysql=8.0
- mysqlclient=2.0.0
# 其他
- 公网ip在db_tunnel.py文件中修改
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