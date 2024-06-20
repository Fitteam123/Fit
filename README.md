# Fit
视动Fit项目页面
# 其他
- 公网ip在db_tunnel.py文件中修改
# 对于接口数据的引用
- from **bakend_test** import generate_data（测试数据引用位于user/consumers.py)
- com.py(连接设备时引用)
# 安装需求
- python=3.9
- pip install -r requirements.txt
# 数据库连接说明
- 不同局域网下使用ssh，同一局域网下注释settings开启通道和关闭通道代码，将端口号和主机ip更改