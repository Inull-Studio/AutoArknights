import socket,threading
sport=[]
socket.setdefaulttimeout(1)
class NewThread(threading.Thread):
    """docstring for NewThread"""
    def __init__(self,target,*args):
        super(NewThread, self).__init__()
        self.func=target
        self.args=args
        self.result=None
    def run(self):
        try:
            self.func(self.args)
            self.result=True
        except:
            self.result=None
    def getresult(self):
        return self.result
def Connects(host,ports:list):
    tlist=[]
    try:
        for port in ports:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            t=NewThread(s.connect,socket.gethostbyname(host),int(port))
            tlist.append(t)
            t.start()
        for t in tlist:
            result=t.getresult()
            if result:
                print(host+str(port),result)
                sport.append(port)
            t.join()
            s.close()
        return sport
    except socket.gaierror:
        return 'unknow HostName'
    except Exception as e:
        return False
if __name__ == '__main__':
    a=Connects('192.168.0.101',['62001','4455','135','1335',60001,61001,63001])
    print(a)