import socket
import threading

sport = []
socket.setdefaulttimeout(0.5)


def _scan(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(host), port))
        s.close()
    except Exception as e:
        pass
    else:
        sport.append(port)


def Connects(host, ports: list):
    tlist = []
    try:
        socket.gethostbyname(host)
        for port in ports:
            t = threading.Thread(target=_scan, args=(host, int(port)))
            tlist.append(t)
            t.start()
        for t in tlist:
            t.join()
    except socket.gaierror:
        return 'unknow hostname'
    return sport if sport else False


if __name__ == '__main__':
    a = Connects('192.168.0.101', [x for x in range(100, 1000)])
    print(a)
