import socket
import threading

sport = []
socket.setdefaulttimeout(1)


# 测试当前主机和端口是否开放，直接使用socket连接
def connScan(host, port):
    try:
        connSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSkt.connect((socket.gethostbyname(host), port))
        connSkt.close()
    except:
        pass
    else:
        sport.append(port)


def Connects(host, ports: list):
    tlist = []
    try:
        socket.gethostbyname(host)
        for port in ports:
            t = threading.Thread(target=connScan, args=(host, int(port)))
            tlist.append(t)
            t.start()
        for t in tlist:
            t.join()
    except socket.gaierror:
        return 'unknow hostname'
    if sport:
        sport.sort()
        return sport
    else:
        return False


if __name__ == '__main__':
    a = Connects('192.168.1.100', [x for x in range(1, 65535)])
    print(a)
