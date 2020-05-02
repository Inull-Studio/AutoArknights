try:
    import cv2
    import PyQt5
except ImportError as e:
    import subprocess
    subprocess.run(['msg', '*', '未找到库模块,正在自动安装'])
    subprocess.run(['pip3', 'insatll', '-r', 'r.txt'])
    subprocess.run(['msg', '*', '自动安装完成'])
    sys.exit(3)
else:
    import sys
    import winreg
    from configparser import ConfigParser
    import os
    import LAN
    from MissionLocation import M_to_L
    import re
    import threading
    from subprocess import run, PIPE
    from os import walk, listdir
    from time import sleep, localtime, strftime
    from PyQt5 import sip
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    import logging
    from tab import Ui_Form
    from test import Ui_MainWindow


class Tab(QWidget, Ui_Form):
    """docstring for Tab"""

    def __init__(self, tabname: str):
        super(Tab, self).__init__()
        self.setupUi(self)
        self.selfmission = False
        self.end = False
        self.LiZhi = {'buhuifu': True, 'yaoji': False, 'yuanshi': False}
        self.Screen_size = []
        self.encoding = str(run(
            ['cmd', '/c', 'chcp'], stdout=PIPE).stdout).strip('\'').strip(r'\n\r').split(' ')[-1]
        self.tabname = tabname
        self.loger = logging.getLogger(tabname)
        self.loger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(
            '.\\Log\\'+tabname+'.log', mode='a', encoding='utf8')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
        self.loger.addHandler(handler)
        self.buhuifu.clicked.connect(self.buhuifu_clicked)
        self.yaoji.clicked.connect(self.yaoji_clicked)
        self.yuanshi.clicked.connect(self.yuanshi_click)
        self.MissionTree.itemClicked.connect(self.Mission_clicked)
        self.Eqlist.itemClicked.connect(lambda: threading.Thread(
            target=self.Eq_clicked, daemon=True).start())
        self.RefreshBtn.clicked.connect(lambda: threading.Thread(
            target=self.testEq, daemon=True).start())
        self.RunBtn.clicked.connect(self.Run_clicked)
        self.EndButon.clicked.connect(self.KillRun)

    def KillRun(self):
        self.end = True

    def Run_clicked(self):
        self.end = False
        if self.SelfMission.isChecked():
            self.setLog(self.tabname, logging.INFO,'开始运行=======================================')
            self.selfmission = True
            mission = M_to_L(self.LiZhi, self.loger, self.LogText)
            threading.Thread(target=self.LoopMission, args=(
                mission,), daemon=True, name='Run').start()
            return
        if not self.Screen_size:
            self.setLog(self.tabname, logging.WARN, '没有选中活动设备')
            return
        if not self.MissionTree.currentItem().text(0):
            self.setLog(self.tabname, logging.WARN, '没有选中关卡')
            return
        self.setLog(self.tabname, logging.INFO,'开始运行=======================================')
        runMission = M_to_L(self.LiZhi, self.loger, self.LogText,
                            self.MissionTree.currentItem().text(0))
        M_location = runMission.retMission()
        threading.Thread(target=self.LoopMission, args=(
            M_location, runMission), daemon=True, name='Run').start()

    def LoopMission(self, runMission=None, M_location=None):
        three_times = 0
        if self.selfmission and not M_location and runMission:
            while True:
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                runMission.selfMission(self.Eqlist.currentItem().text().split('\t')[
                                       0], self.Screen_size)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                sleep(0.5)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                lizhi = runMission.checklizhi(
                    self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                if not lizhi:
                    self.setLog(self.tabname, logging.INFO, '理智自动执行成功')
                    if self.end:
                        self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                        return
                    pass
                elif lizhi == 'buhuifu':
                    self.setLog(self.tabname, logging.INFO, '不自动恢复理智,停止自动刷=======================')
                    if self.end:
                        self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                        return
                    return
                else:
                    return
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                run(['adb.exe', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input', 'tap',
                     str(int(self.Screen_size[0]*(10/12))), str(int(self.Screen_size[1]*(25/36)))], stdout=PIPE)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                self.setLog(self.tabname, logging.INFO, '开始运行,60秒后循环检测运行状态,60秒内不能结束')
                sleep(60)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                if self.end:
                    self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                    return
                while True:
                    if self.end:
                        self.setLog(self.tabname, logging.INFO,'结束运行=======================================')
                        return
                    if runMission.shengji(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                        self.setLog(self.tabname, logging.INFO, '检测到升级,正在自动点击')
                        if self.end:
                            self.setLog(self.tabname, logging.INFO, '结束运行=======================================')
                            return
                        break
                    three = runMission.sanxing(
                        self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                    if 'N' in three:
                        three_times += 1
                        if three_times == 3:
                            self.setLog(self.tabname, logging.ERROR, '非三星次数过多,已停止===================')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        if self.end:
                            self.setLog(self.tabname, logging.INFO, '结束运行=======================================')
                            return
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        if self.end:
                            self.setLog(self.tabname, logging.INFO, '结束运行=======================================')
                            return
                        sleep(8)
                        break
                    else:
                        pass
                    pass
        else:
            while True:
                if not M_location(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                    return
                sleep(0.5)
                lizhi = runMission.checklizhi(
                    self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                if not lizhi:
                    self.setLog(self.tabname, logging.INFO, '理智自动执行成功')
                    pass
                elif lizhi == 'buhuifu':
                    self.setLog(self.tabname, logging.INFO, '不自动恢复理智,停止自动刷=======================')
                    return
                else:
                    return
                if self.end:
                    self.setLog(self.tabname, logging.INFO,
                                '结束运行=======================================')
                    return
                run(['adb.exe', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input', 'tap',
                     str(int(self.Screen_size[0]*(10/12))), str(int(self.Screen_size[1]*(25/36)))], stdout=PIPE)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,
                                '结束运行=======================================')
                    return
                self.setLog(self.tabname, logging.INFO, '开始运行,60秒后循环检测运行状态,60秒内不能结束')
                if self.end:
                    self.setLog(self.tabname, logging.INFO,
                                '结束运行=======================================')
                    return
                sleep(60)
                if self.end:
                    self.setLog(self.tabname, logging.INFO,
                                '结束运行=======================================')
                    return
                while True:
                    if runMission.shengji(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                        self.setLog(self.tabname, logging.INFO, '检测到升级,正在自动点击')
                        break
                    three = runMission.sanxing(
                        self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                    if 'N' in three:
                        three_times += 1
                        if three_times == 3:
                            self.setLog(
                                self.tabname, logging.ERROR, '非三星次数过多,已停止===================')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        sleep(8)
                        break
                    else:
                        pass
                    pass

    def Eq_clicked(self):
        self.setLog(self.tabname, logging.INFO, '正在选择设备、测试')
        self.Screen_size = [int(x) for x in run(['adb.exe', '-s', '{}'.format(self.Eqlist.currentItem().text().split('\t')[0]),
                                                 'shell', 'wm', 'size'], stdout=PIPE, encoding=self.encoding).stdout.split('\n')[0].split(' ')[-1].split('x')[::-1]]
        if not self.Screen_size[0]:
            self.setLog(self.tabname, logging.INFO, self.Eqlist.currentItem(
            ).text().split('\t')[0]+' 未知错误,设备无法连接')
            self.Screen_size = []
            return
        self.setLog(self.tabname, logging.INFO,
                    self.Eqlist.currentItem().text().split('\t')[0]+' 已选择')

    def Mission_clicked(self):
        self.setLog(self.tabname, logging.INFO,
                    self.MissionTree.currentItem().text(0)+' 已选择')

    def testEq(self):
        self.Eqlist.clear()
        eq_list = []
        self.setLog(self.tabname, logging.INFO,self.Eqlist.objectName()+' 正在测试设备连接,请稍等')
        Tlist = []
        def Connect(port,host='127.0.0.1'):
            run(['adb.exe', 'connect', f'{host}:{port}'], stdout=PIPE)
        hosts=con.get('Nox','rhost')
        if not hosts:
            ports = eval(con.get('Nox', 'portlist'))
            for port in ports:
                t = threading.Thread(target=Connect, args=(port,))
                Tlist.append(t)
                t.start()
            for t in Tlist:
                t.join()
            for l in run(['adb.exe', 'devices'], stdout=PIPE, encoding=self.encoding).stdout.rstrip('\n').split('\n'):
                if 'List' in l.split(' '):
                    continue
                if 'offline' in l:
                    continue
                b = l.split('\t')[0]
                if '127.0.0.1' in b:
                    eq_list.append(b+'\t模拟器')
                else:
                    eq_list.append(b+'\t手机')
            self.setLog(self.tabname, logging.INFO,
                        self.Eqlist.objectName()+' 测试完成')
            if not eq_list:
                self.setLog(self.tabname, logging.INFO,
                            self.Eqlist.objectName()+' 未检测到设备开启,请重新运行')
            else:
                self.Eqlist.addItems(eq_list)
        else:
            host=eval(host)
            ports=eval(con.get('Nox','rport'))
            for port in ports:
                for host in hosts:
                    t = threading.Thread(target=Connect, args=(port,host))
                    Tlist.append(t)
                    t.start()
            for t in Tlist:
                t.join()
            for l in run(['adb.exe', 'devices'], stdout=PIPE, encoding=self.encoding).stdout.rstrip('\n').split('\n'):
                if 'List' in l.split(' '):
                    continue
                if 'offline' in l:
                    continue
                b = l.split('\t')[0]
                for host in hosts:
                    if '127.0.0.1' in b:
                        eq_list.append(b+'\t模拟器')
                    elif host in b:
                        eq_list.app(b+'\t模拟器')
                    else:
                        eq_list.append(b+'\t手机')
            self.setLog(self.tabname, logging.INFO,
                        self.Eqlist.objectName()+' 测试完成')
            if not eq_list:
                self.setLog(self.tabname, logging.INFO,
                            self.Eqlist.objectName()+' 未检测到设备开启,请重新运行')
            else:
                self.Eqlist.addItems(eq_list)

    def buhuifu_clicked(self):
        self.LiZhi['buhuifu'] = True
        self.LiZhi['yaoji'] = False
        self.LiZhi['yuanshi'] = False
        self.setLog(self.tabname, logging.INFO, self.buhuifu.text()+' 已选择')

    def yuanshi_click(self):
        self.LiZhi['yuanshi'] = True
        self.LiZhi['buhuifu'] = False
        self.LiZhi['yaoji'] = False
        self.setLog(self.tabname, logging.INFO, self.yuanshi.text()+' 已选择')

    def yaoji_clicked(self):
        self.LiZhi['yaoji'] = True
        self.LiZhi['buhuifu'] = False
        self.LiZhi['yuanshi'] = False
        self.setLog(self.tabname, logging.INFO, self.yaoji.text()+' 已选择')

    def setLog(self, tabname, level, msg):
        logmsg = f'{level} {tabname}.{msg}'
        self.loger.log(level, f'{tabname}.{msg}')
        self.LogText.append(logmsg)


class MainWin(QMainWindow, Ui_MainWindow):
    """None"""

    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        QTextCodec.setCodecForLocale(QTextCodec.codecForName('utf8'))
        self.setupUi(self)
        self.firstCheck()
        self.CreateTab.triggered.connect(self.addNewTab)
        self.DeleteTab.triggered.connect(self.delTab)
        self.Scan.triggered.connect(self.ScanEq)
        self.DeleteAllLog.triggered.connect(self.delLog)
        self.Help.triggered.connect(self.showHelp)
        self.Author.triggered.connect(self.showAuthor)
        self.Soft.triggered.connect(self.showSoft)
        self.UnScan.triggered.connect(self.delConfig)
        self.RemoteScan.triggered.connect(self.RS)

    def RS(self):
        lasthost=[]
        lastport=[]
        if con.get('Nox','portlist'):
            portlist=eval(con.get('Nox','portlist'))
            host,ok=QInputDialog.getText(self, '输入主机', '请输入主机名或IP地址\n127.0.0.1本地ip就不用输了,浪费性能和资源')
            if ok:
                if not host:
                    QMessageBox.warning(self, '错误', '未输入主机名或IP地址')
                else:
                    if not con.get('Nox','rport'):
                        result=LAN.Connect(host,portlist)
                        if not result:
                            QMessageBox.warning(self,'错误','未开启模拟器')
                        elif 'unknow' in result:
                            QMessageBox.warning(self,'错误','未知的主机名或IP地址')
                        else:
                            con.set('Nox','rhost','[\''+host+'\']')
                            con.set('Nox','rport',str(list(set(result))))
                            con.write(open('config.ini','w'))
                            QMessageBox.information(self,'完成','远程主机扫描完成，刷新设备会检测链接')
                    else:
                        result=LAN.Connect(host,portlist)
                        if not result:
                            QMessageBox.warning(self,'错误','未开启模拟器')
                        elif 'unknow' in result:
                            QMessageBox.warning(self,'错误','未知的主机名或IP地址')
                        else:
                            lasthost+=eval(con.get('Nox','rhost'))
                            lasthost.append(host)
                            lastport+=eval(con.get('Nox','rport'))
                            lastport+=(list(set(result)))
                            con.set('Nox','rhost',str(list(set(lasthost))))
                            con.set('Nox','rport',str(list(set(lastport))))
                            con.write(open('config.ini','w'))
                            QMessageBox.information(self,'完成','远程主机扫描完成，刷新设备会检测链接')
        else:
            self.ScanEq()
            self.RS()


    def delConfig(self):
        if con.get('Nox','dir'):
            con.set('Nox','dir','')
            con.set('Nox','portlist','')
            con.set('Nox','rhost','')
            con.set('Nox','rport','')
            con.write(open('config.ini','w'))
        QMessageBox.information(self,'通知','已经删除config.ini配置')

    def firstCheck(self):
        if not os.path.exists('.\\Log'):
            os.mkdir('Log')
        if not os.path.exists('.\\Data'):
            os.mkdir('Data')

    def __listPort(self):
        if not con.get('Nox', 'dir'):
            try:
                i=0
                while True:
                    name,value,type=winreg.EnumValue(key,i)
                    if 'Nox.exe' in name:
                        con.set('Nox','dir','\\'.join(name.split('\\')[:-1]))
                        con.write(open('config.ini','w'))
                        break
                    i+=1
            except WindowsError:
                pass
            self.__listPort()
        elif not con.get('Nox', 'portlist'):
            dir = con.get('Nox', 'dir')
            portList = []
            for file in listdir(rf'{dir}\BignoxVMS'):
                portList += [x[0] for x in re.findall('hostport="(\d*)" guestport="(\d*)"', open(rf'{dir}\BignoxVMS\{file}\{file}.vbox', 'r').read())]
            portList = list(set(portList))
            con.set('Nox', 'portlist', str(portList))
            con.write(open('config.ini', 'w'))
            self.__listPort()
        elif con.get('Nox', 'dir') and con.get('Nox', 'portlist'):
            QMessageBox.information(self, '已存在', '设备已扫描完成')
        else:
            raise FileNotFoundError('夜神模拟器不存在')

    def delLog(self):
        try:
            os.chdir('Log')
            [os.remove(f) for f in os.listdir()]
            os.chdir('..')
        except:
            QMessageBox.warning(self, '错误', '请关闭程序再重试')

    def showHelp(self):
        QMessageBox.about(self, '使用帮助', '''
            Config.ini和软件本身是重要文件，必须存在，如果不存在会报错
            单击"菜单"->"新建"，可以新建一个链接，可以建立无限多个，只要你电脑承受的住，链接是自动运行的必备框架，一个链接代表着一个明日方舟
            单击"菜单"->"删除"，可以删除当前所在链接，单击"设置"->"删除所有日志文件"，可以删除Log文件夹下的所有日志，必须是在刚启动软件时才能点击
            单击"设备"->"扫描"，可以扫描夜神模拟器所在目录和夜神模拟器多开数量，每多开一个模拟器必须删除扫描结果，然后重新扫描
            更多详细资料请在 Help.chm 中查看''')

    def showAuthor(self):
        QMessageBox.about(self, '关于作者', '''
            作者邮箱：2293830442@qq.com
            作者Github：https://github.com/basket-ball
            作者bilibili：https://space.bilibili.com/16057264
            作者CSDN：https://blog.csdn.net/qq_40173711
            有任何问题请联系邮箱，QQ不加任何人的''')

    def showSoft(self):
        QMessageBox.about(self, '关于软件', '版权所有CopyRight © 2020 basket_ball')

    def ScanEq(self):
        try:
            self.__listPort()
        except FileNotFoundError:
            QMessageBox.warning(self, '文件缺失', '缺少关键文件,请验证程序完整性')
        except:
            QMessageBox.warning(self, '模拟器不存在', '夜神模拟器不存在,将会测试手机连通性')

    def delTab(self):
        self.MainTab.removeTab(self.MainTab.currentIndex())
        del self.MainTab.children()[0].children()[
            self.MainTab.currentIndex()+1]

    def addNewTab(self):
        tabname, ok = QInputDialog.getText(self, '输入名称', '请输入新建标签页名称')
        if ok:
            if not tabname:
                QMessageBox.warning(self, '名称错误', '未知的标签名')
            else:
                NewTab = Tab(tabname)
                NewTab.setObjectName(tabname)
                self.Log = logging.getLogger()
                self.MainTab.addTab(NewTab, tabname)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        win = MainWin()
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched')
        if not os.path.exists('config.ini'):
            raise FileNotFoundError
        con = ConfigParser()
        con.read('config.ini', encoding='utf8')
        threading.Thread(target=win.show(), daemon=True).start()
        sys.exit(app.exec_())
    except FileNotFoundError:
        QMessageBox.warning(win, '错误', '未找到config.ini\n请验证文件完整性')
        sys.exit(2)
    except Exception as e:
        print(e)
