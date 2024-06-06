from sshtunnel import SSHTunnelForwarder

def create_ssh_tunnel():
    server = SSHTunnelForwarder(
        ('127.0.0.1', 22),  # SSH服务器的主机和端口
        ssh_username='15777343141@163.com',
        ssh_password='czy20020922',
        remote_bind_address=('127.0.0.1', 3306)  # MySQL服务器的主机和端口
    )
    server.start()
    return server
