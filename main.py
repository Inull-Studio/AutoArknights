import sys
import winreg,json
import ctypes,inspect
from configparser import ConfigParser
import os
import shutil,Material
import LAN
from MissionLocation import M_to_L
import re
import six
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
import threading
from subprocess import run, PIPE
from os import walk, listdir, popen
from time import sleep, localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
from tab import Ui_Form
from test import Ui_MainWindow
from Plan import Ui_Dialog as Plan_Dialog
from Report import Ui_Dialog as Report_Dialog

logLevel = {10: 'DEBUG', 20: 'INFO', 30: 'WARN', 40: 'ERROR', 50: 'CRITICAL'}


class Tab(QWidget, Ui_Form):
    """docstring for Tab"""

    def __init__(self, tabname: str, parent=None):
        super(Tab, self).__init__(parent)
        self.setupUi(self)
        self.xianzhi = 1
        self.selfmission = False
        self.running=None
        self.running_mission=None
        self.run_times=0
        self.LiZhi = {'buhuifu': True, 'yaoji': False, 'yuanshi': False}
        self.Screen_size = []
        self.encoding = str(run(['cmd', '/c', 'chcp'], stdout=PIPE).stdout).strip('\'').strip(r'\n\r').split(' ')[-1]
        self.tabname = tabname
        self.loger = logging.getLogger(tabname)
        self.loger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('.\\Log\\'+tabname+'.log', mode='a', encoding='utf8')
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
        self.Times.valueChanged.connect(self.xianzhiTimes)
        self.threeTimes.valueChanged.connect(self.showThreeTimes)

    def showThreeTimes(self):
        self.setLog(self.tabname, logging.INFO,
                    '设置限制三星次数为{}'.format(self.threeTimes.value()))

    def xianzhiTimes(self):
        self.xianzhi = self.Times.value()
        self.setLog(self.tabname, logging.INFO,
                    '设置限制运行次数为{}'.format(self.Times.value()))

    def KillRun(self):
        try:
            if self.running:
                self._async_raise(self.running,SystemExit)
                self.setLog(self.tabname, logging.INFO,'=====结束运行=====')
                self.running=None
                self.run_times=0
                self.running_mission=None
        except Exception as e:
            self.setLog(self.tabname,logging.WARNING,'进程未结束')

    def _async_raise(self,thread, exctype):
        """raises the exception, performs cleanup if needed"""
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def Run_clicked(self):
        if self.running:
            self.setLog(self.tabname,logging.INFO,'正在运行中，请不要重复运行')
            return
        self.setLog(self.tabname, logging.INFO,'=====开始运行=====')
        if self.SelfMission.isChecked():
            self.selfmission = True
            mission = M_to_L(self.LiZhi, self.loger, self.LogText)
            self.running = threading.Thread(target=self.LoopMission, args=(mission,), daemon=True, name=self.tabname)
            self.running.start()
            return
        if not self.Screen_size:
            self.setLog(self.tabname, logging.WARN, '没有选中活动设备')
            return
        if not self.MissionTree.currentItem().text(0):
            self.setLog(self.tabname, logging.WARN, '没有选中关卡')
            return
        runMission = M_to_L(self.LiZhi, self.loger, self.LogText,self.MissionTree.currentItem().text(0))
        M_location = runMission.retMission()
        self.running = threading.Thread(target=self.LoopMission, args=(M_location, runMission), daemon=True, name=self.tabname)
        self.running.start()

    def LoopMission(self, runMission=None, M_location=None):
        three_times = 0
        self.running_mission=self.MissionTree.currentItem().text(0)
        if self.selfmission and not M_location and runMission:
            while self.xianzhi:
                if not self.buxianzhi.isChecked():
                    self.xianzhi -= 1
                runMission.selfMission(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                sleep(0.5)
                lizhi = runMission.checklizhi(
                    self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                if not lizhi:
                    self.setLog(self.tabname, logging.INFO, '理智自动执行成功')
                    pass
                elif lizhi == 'buhuifu':
                    self.setLog(self.tabname, logging.INFO,
                                '不自动恢复理智,停止自动刷=============')
                    return

                run(['adb.exe', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input', 'tap',str(int(self.Screen_size[0]*(10/12))), str(int(self.Screen_size[1]*(25/36)))], stdout=PIPE)
                self.setLog(self.tabname, logging.INFO,
                            '进入关卡,60秒后循环检测运行状态')
                sleep(60)
                while True:
                    if runMission.shengji(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                        self.setLog(self.tabname, logging.INFO, '检测到升级,正在自动点击')
                    three = runMission.sanxing(
                        self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                    if 'N' in three:
                        if not self.checkThree.isChecked():
                            three_times += 1
                        if three_times == self.threeTimes.value():
                            self.setLog(self.tabname, logging.ERROR,
                                        '非三星次数过多,已停止===============')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        self.run_times+=1
                        self.save_Mission()
                        sleep(8)
                        break
                    pass
        else:
            while self.xianzhi:
                if not self.buxianzhi.isChecked():
                    self.xianzhi -= 1
                if not M_location(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                    return
                sleep(0.5)
                lizhi = runMission.checklizhi(
                    self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                if not lizhi:
                    self.setLog(self.tabname, logging.INFO, '理智自动执行成功')
                    pass
                elif lizhi == 'buhuifu':
                    self.setLog(self.tabname, logging.INFO,
                                '不自动恢复理智,停止自动刷=========')
                    return
                else:
                    return
                run(['adb.exe', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input', 'tap',
                     str(int(self.Screen_size[0]*(10/12))), str(int(self.Screen_size[1]*(25/36)))], stdout=PIPE)
                self.setLog(self.tabname, logging.INFO,
                            '进入关卡,60秒后循环检测运行状态')
                sleep(60)
                while True:
                    if runMission.shengji(self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size):
                        self.setLog(self.tabname, logging.INFO, '检测到升级,正在自动点击')
                        break
                    three = runMission.sanxing(
                        self.Eqlist.currentItem().text().split('\t')[0], self.Screen_size)
                    if 'N' in three:
                        if not self.checkThree.isChecked():
                            three_times += 1
                        if three_times == self.threeTimes.value():
                            self.setLog(self.tabname, logging.ERROR,
                                        '非三星次数超限制,已停止=====')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        self.run_times+=1
                        self.save_Mission()
                        sleep(8)
                        break
                    pass
        self.setLog(self.tabname, logging.INFO, '运行完成')

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
        self.setLog(self.tabname, logging.INFO,
                    self.Eqlist.objectName()+' 正在测试设备连接,请稍等')
        Tlist = []

        def Connect(port, host='127.0.0.1'):
            run(['adb.exe', 'connect', f'{host}:{port}'], stdout=PIPE)
        rhosts = con.get('Nox', 'rhost')
        lports = con.get('Nox', 'portlist')
        if lports:
            for port in eval(lports):
                t = threading.Thread(target=Connect, args=(port,),daemon=True)
                QApplication.processEvents()
                Tlist.append(t)
                t.start()
            for t in Tlist:
                QApplication.processEvents()
                t.join()
            for l in run(['adb.exe', 'devices'], stdout=PIPE, encoding='utf8').stdout.rstrip('\n').split('\n'):
                QApplication.processEvents()
                if 'List' in l.split(' '):
                    continue
                if 'offline' in l:
                    continue
                b = l.split('\t')[0]
                if '127.0.0.1' in b:
                    eq_list.append(b+'\t模拟器')
                else:
                    eq_list.append(b+'\t手机')
        else:
            self.setLog(self.tabname, logging.WARNING, '本地未有设备(未扫描本地模拟器)')
        if rhosts:
            rports = con.get('Nox', 'rport')
            if rports:
                for port in eval(rports):
                    for host in eval(rhosts):
                        t = threading.Thread(target=Connect, args=(port, host))
                        Tlist.append(t)
                        t.start()
                        QApplication.processEvents()
                for t in Tlist:
                    QApplication.processEvents()
                    t.join()
                    QApplication.processEvents()
                for l in run(['adb.exe', 'devices'], stdout=PIPE, encoding='utf8').stdout.rstrip('\n').split('\n'):
                    QApplication.processEvents()
                    if 'List' in l.split(' '):
                        continue
                    if 'offline' in l:
                        continue
                    b = l.split('\t')[0]
                    for host in eval(rhosts):
                        for port in eval(rports):
                            QApplication.processEvents()
                            if '127.0.0.1' in b:
                                eq_list.append(b+'\t模拟器')
                            elif host in b and int(port) > 50000:
                                eq_list.append(b+'\t模拟器')
                            else:
                                eq_list.append(b+'\t手机')
                self.setLog(self.tabname, logging.INFO,
                            self.Eqlist.objectName()+' 测试完成')
                eq_list = list(set(eq_list))
                if not eq_list:
                    self.setLog(self.tabname, logging.INFO,
                                self.Eqlist.objectName()+' 未检测到设备开启,请重新运行')
                else:
                    self.Eqlist.addItems(eq_list)
            else:
                self.setLog(self.tabname, logging.WARNING, '远程地址未有设备(未扫远程描模)')
                return

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
    def save_Mission(self):
        if not os.path.isfile(f'Data\\{self.tabname}_{self.running_mission}_{self.run_times}.png'):
            shutil.copy('temp_Data\\three.png',f'Data\\{self.tabname}_{self.running_mission}_{self.run_times}.png')

    def setLog(self, tabname, level, msg):
        logmsg = f'{logLevel[level]} {tabname}.{msg}'
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
        self.add_plan.triggered.connect(self.append_plan)

    def append_plan(self):
        self.d=QDialog()
        item=Plan_Dialog()
        item.setupUi(self.d)
        aa=self.d.exec()
        if aa==QDialog.Accepted:
            print(item.count.value())
            print(item.item_name.currentText())
    def RS(self):
        lasthost = []
        lastport = []
        host, hok = QInputDialog.getText(
            self, '输入主机', '请输入主机名或IP地址\n127.0.0.1本地ip就不用输了,浪费性能和资源\n%注意！如果配置文件中存在本地端口，则会使用本地端口进行测试%\n%可能会造成检测不到!%')
        if hok:
            if not host:
                QMessageBox.warning(self, '错误', '未输入主机名或IP地址')
                return
            else:
                if con.get('Nox', 'portlist'):
                    a = QMessageBox(QMessageBox.Question,'是否使用本地端口','检测到本地存在模拟器\n是否用本地端口扫描远程端口?(这可能会导致扫描不到远程模拟器,因为端口原因,但是方便)',QMessageBox.Yes | QMessageBox.No)
                    ok = a.exec()
                    if ok == QMessageBox.Yes:
                        portlist = eval(con.get('Nox', 'portlist'))
                        if not con.get('Nox', 'rport'):
                            result = LAN.Connects(host, portlist)
                            if not result:
                                QMessageBox.warning(self, '错误', '未开启模拟器')
                            elif 'unknow' in result:
                                QMessageBox.warning(self, '错误', '未知的主机名或IP地址')
                            else:
                                con.set('Nox', 'rhost', '[\''+host+'\']')
                                con.set('Nox', 'rport', str(list(set(result))))
                                con.write(open('config.ini', 'w'))
                                QMessageBox.information(
                                    self, '完成', '远程主机扫描完成，刷新设备会检测链接')
                        else:
                            result = LAN.Connects(host, portlist)
                            if not result:
                                QMessageBox.warning(self, '错误', '未开启模拟器')
                            elif 'unknow' in result:
                                QMessageBox.warning(self, '错误', '未知的主机名或IP地址')
                            else:
                                lasthost += eval(con.get('Nox', 'rhost'))
                                lasthost.append(host)
                                lastport += eval(con.get('Nox', 'rport'))
                                lastport += (list(set(result)))
                                con.set('Nox', 'rhost', str(
                                    list(set(lasthost))))
                                con.set('Nox', 'rport', str(
                                    list(set(lastport))))
                                con.write(open('config.ini', 'w'))
                                QMessageBox.information(
                                    self, '完成', '远程主机扫描完成，刷新设备会检测链接')
                    else:
                        port, pok = QInputDialog.getInt(
                            self, '输入端口号', '请输入远程主机模拟器所开启的端口')
                        if pok:
                            if not port or port > 65535 or port < 0:
                                QMessageBox.warning(
                                    self, '错误', '为输入端口号,或端口号不正确')
                                return
                            if not con.get('Nox', 'rport'):
                                result = LAN.Connects(host, [port])
                                if not result:
                                    QMessageBox.warning(self, '错误', '未开启模拟器')
                                elif 'unknow' in result:
                                    QMessageBox.warning(
                                        self, '错误', '未知的主机名或IP地址')
                                else:
                                    con.set('Nox', 'rhost', '[\''+host+'\']')
                                    con.set('Nox', 'rport', str(
                                        list(set(result))))
                                    con.write(open('config.ini', 'w'))
                                    QMessageBox.information(
                                        self, '完成', '远程主机扫描完成，刷新设备会检测链接')
                            else:
                                result = LAN.Connects(host, [port])
                                if not result:
                                    QMessageBox.warning(self, '错误', '未开启模拟器')
                                elif 'unknow' in result:
                                    QMessageBox.warning(
                                        self, '错误', '未知的主机名或IP地址')
                                else:
                                    lasthost += eval(con.get('Nox', 'rhost'))
                                    lasthost.append(host)
                                    lastport += eval(con.get('Nox', 'rport'))
                                    lastport += (list(set(result)))
                                    con.set('Nox', 'rhost', str(
                                        list(set(lasthost))))
                                    con.set('Nox', 'rport', str(
                                        list(set(lastport))))
                                    con.write(open('config.ini', 'w'))
                                    QMessageBox.information(
                                        self, '完成', '远程主机扫描完成，刷新设备会检测链接')
                else:
                    port, pok = QInputDialog.getInt(
                        self, '输入端口号', '请输入远程主机模拟器所开启的端口')
                    if pok:
                        if not port or port > 65535 or port < 0:
                            QMessageBox.warning(self, '错误', '为输入端口号,或端口号不正确')
                            return
                        if not con.get('Nox', 'rport'):
                            result = LAN.Connects(host, [port])
                            if not result:
                                QMessageBox.warning(self, '错误', '未开启模拟器')
                            elif 'unknow' in result:
                                QMessageBox.warning(self, '错误', '未知的主机名或IP地址')
                            else:
                                con.set('Nox', 'rhost', '[\''+host+'\']')
                                con.set('Nox', 'rport', str(list(set(result))))
                                con.write(open('config.ini', 'w'))
                                QMessageBox.information(
                                    self, '完成', '远程主机扫描完成，刷新设备会检测链接')
                        else:
                            result = LAN.Connects(host, [port])
                            if not result:
                                QMessageBox.warning(self, '错误', '未开启模拟器')
                            elif 'unknow' in result:
                                QMessageBox.warning(self, '错误', '未知的主机名或IP地址')
                            else:
                                lasthost += eval(con.get('Nox', 'rhost'))
                                lasthost.append(host)
                                lastport += eval(con.get('Nox', 'rport'))
                                lastport += (list(set(result)))
                                con.set('Nox', 'rhost', str(
                                    list(set(lasthost))))
                                con.set('Nox', 'rport', str(
                                    list(set(lastport))))
                                con.write(open('config.ini', 'w'))
                                QMessageBox.information(
                                    self, '完成', '远程主机扫描完成，刷新设备会检测链接')

    def delConfig(self):
        if con.get('Nox', 'dir'):
            con.set('Nox', 'dir', '')
            con.set('Nox', 'portlist', '')
            con.set('Nox', 'rhost', '')
            con.set('Nox', 'rport', '')
            con.write(open('config.ini', 'w'))
        QMessageBox.information(self, '通知', '已经删除config.ini配置')

    def firstCheck(self):
        if not os.path.exists('.\\Log'):
            os.mkdir('Log')
        if not os.path.exists('.\\Data'):
            os.mkdir('Data')

    def __listPort(self):
        if not con.get('Nox', 'dir'):
            try:
                i = 0
                while True:
                    name, value, type = winreg.EnumValue(key, i)
                    if 'Nox.exe' in name:
                        con.set('Nox', 'dir', '\\'.join(name.split('\\')[:-1]))
                        con.write(open('config.ini', 'w'))
                        break
                    i += 1
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
            return
        else:
            raise FileNotFoundError('夜神模拟器不存在')

    def delLog(self):
        try:
            os.chdir('Log')
            [os.remove(f) for f in os.listdir()]
            os.chdir('..')
        except:
            QMessageBox.critical(self, '错误', '请关闭程序再重试')

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
            QMessageBox.critical(self, '文件缺失', '缺少关键文件,请验证程序完整性')
        except:
            QMessageBox.warning(self, '模拟器不存在', '夜神模拟器不存在,在链接内刷新设备可连接手机/或点击远程扫描')

    def delTab(self):
        self.MainTab.removeTab(self.MainTab.currentIndex())
        del self.MainTab.children()[0].children()[
            self.MainTab.currentIndex()+1]

    def addNewTab(self):
        tabname, ok = QInputDialog.getText(self, '输入名称', '请输入新建标签页名称')
        if ok:
            if not tabname:
                QMessageBox.critical(self, '名称错误', '未知的标签名')
            else:
                NewTab = Tab(tabname)
                NewTab.setObjectName(tabname)
                self.MainTab.addTab(NewTab, tabname)


if __name__ == '__main__':
    try:
        os.chdir(popen('cd').read().strip('\n'))
        popen('adb nodaemon server')
        app = QApplication(sys.argv)
        win = MainWin()
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched')
        if not os.path.exists('config.ini'):
            raise FileNotFoundError
        con = ConfigParser()
        con.read('config.ini', encoding='utf8')
        threading.Thread(target=win.show(), daemon=True).start()
        sys.exit(app.exec_())
    except FileNotFoundError:
        QMessageBox.critical(win, '错误', '未找到config.ini\n请验证文件完整性')
        sys.exit(2)
    except Exception as e:
        print(e)
