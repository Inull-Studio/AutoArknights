import socket,threading

sport=[]
socket.setdefaulttimeout(0.1)
def scan(host,port):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(host),port))
        s.close()
    except:
        pass
    else:
        sport.append(port)
def Connects(host,ports:list):
    tlist=[]
    try:
        socket.gethostbyname(host)
        for port in ports:
            t=threading.Thread(target=scan,args=(host,int(port)))
            tlist.append(t)
            t.start()
        for t in tlist:
            t.join()
    except socket.gaierror:
        return 'unknow hostname'
    return sport if sport else False
if __name__ == '__main__':
    a=Connects('1.1.1.1',[x for x in range(100,1000)])
    print(a)