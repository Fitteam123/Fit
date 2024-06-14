import redis

# 测试连接
client = redis.StrictRedis(host='localhost', port=6379, db=0)
print(client.ping())  # 输出 PONG
