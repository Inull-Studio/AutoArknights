# coding:utf-8
import sys
import winreg
import json
import win32gui
import win32api
import ctypes
import inspect
from configparser import ConfigParser
import os
import shutil
import Material
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
from time import sleep, strftime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
from tab import Ui_Form
from mainGUI import Ui_MainWindow
from Plan import Ui_Dialog as Plan_Dialog
from Report import Ui_Dialog as Report_Dialog
from plan_option import Ui_Dialog as PlanOption_Dialog
from R_Plan import Ui_Dialog as Rp_Dialog
from R_Report import Ui_Dialog as Rr_Dialog

logLevel = {10: 'DEBUG', 20: 'INFO', 30: 'WARN', 40: 'ERROR', 50: 'CRITICAL'}


class Tab(QWidget, Ui_Form):
    """AutoArknights的核心界面"""

    def __init__(self, tabname: str, parent=None):
        """"""
        super(Tab, self).__init__(parent)
        self.setupUi(self)
        self.three_times = 0
        self.xianzhi = 1
        self.selfmission = False
        self.running = None
        self.device_name = ''
        self.running_mission = None
        self.run_times = 0
        self.LiZhi = {'buhuifu': True, 'yaoji': False, 'yuanshi': False}
        self.Screen_size = []
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
        self.RefreshBtn.clicked.connect(
            lambda: threading.Thread(target=self.testEq).start())
        self.RunBtn.clicked.connect(self.Run_clicked)
        self.EndButon.clicked.connect(self.KillRun)
        self.Times.valueChanged.connect(self.xianzhiTimes)
        self.threeTimes.valueChanged.connect(self.showThreeTimes)
        self.disp_btn.clicked.connect(self.disp)

    def disp(self):
        if not self.device_name:
            self.setLog(self.tabname, logging.WARNING, '未选择设备')
            return
        hwnd = win32gui.FindWindow('SDL_app', self.device_name)
        if hwnd != 0:
            self.setLog(self.tabname, logging.INFO, '正在显示,不能重复显示')
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, 1)
            return
        win32api.ShellExecute(
            0, None, r'.\Data\tools\scrcpy-noconsole', '-n', None, 1)

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
                self._async_raise(self.running, SystemExit)
                self.setLog(self.tabname, logging.INFO, '=====结束运行=====')
                self.running = None
                self.run_times = 0
                self.running_mission = None
        except:
            self.setLog(self.tabname, logging.WARNING, '进程未结束')

    def _async_raise(self, thread, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(thread.ident)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread.ident, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def Run_clicked(self):
        if self.running:
            self.setLog(self.tabname, logging.INFO, '正在运行中，请不要重复运行')
            return
        self.setLog(self.tabname, logging.INFO, '=====开始运行=====')
        if self.SelfMission.isChecked():
            self.selfmission = True
            mission = M_to_L(self.LiZhi, self.loger, self.LogText)
            self.running = threading.Thread(target=self.LoopMission, args=(
                mission,), daemon=True, name=self.tabname)
            self.running.start()
            return
        if not self.Screen_size:
            self.setLog(self.tabname, logging.WARN, '没有选中活动设备')
            return
        if not self.MissionTree.currentItem().text(0):
            self.setLog(self.tabname, logging.WARN, '没有选中关卡')
            return
        runMission = M_to_L(self.LiZhi, self.loger, self.LogText,
                            self.MissionTree.currentItem().text(0))
        M_location = runMission.retMission()
        self.running = threading.Thread(target=self.LoopMission, args=(
            M_location, runMission), daemon=True, name=self.tabname)
        self.running.start()

    def LoopMission(self, runMission=None, M_location=None):
        if self.selfmission and not M_location and runMission:
            self.running_mission = 'self'
            while self.xianzhi:
                if not self.buxianzhi.isChecked():
                    self.xianzhi -= 1
                runMission.selfMission(self.Eqlist.currentItem().text().split('\t')[
                                       0], self.Screen_size)
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

                run([r'.\Data\tools\adb', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input',
                     'tap', str(int(self.Screen_size[0]*(10/12))), str(int(self.Screen_size[1]*(25/36)))], stdout=PIPE)
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
                            self.three_times += 1
                        if self.three_times == self.threeTimes.value():
                            self.setLog(self.tabname, logging.ERROR,
                                        '非三星次数过多,已停止===============')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        self.run_times += 1
                        self.save_Mission()
                        sleep(8)
                        break
                    pass
        else:
            self.running_mission = self.MissionTree.currentItem().text()
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
                run([r'.\Data\tools\adb', '-s', self.Eqlist.currentItem().text().split('\t')[0], 'shell', 'input', 'tap',
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
                            self.three_times += 1
                        if self.three_times == self.threeTimes.value():
                            self.setLog(self.tabname, logging.ERROR,
                                        '非三星次数超限制,已停止=====')
                            return
                        self.setLog(self.tabname, logging.WARN, '检测到未三星')
                        break
                    elif 'Y' in three:
                        self.setLog(self.tabname, logging.INFO, '是三星')
                        self.run_times += 1
                        self.save_Mission()
                        sleep(8)
                        break
                    pass
        self.setLog(self.tabname, logging.INFO, '运行完成')

    def Eq_clicked(self):
        self.setLog(self.tabname, logging.INFO, '正在选择设备、测试')
        self.Screen_size = [int(x) for x in run([r'.\Data\tools\adb', '-s', '{}'.format(self.Eqlist.currentItem().text().split(
            '\t')[0]), 'shell', 'wm', 'size'], stdout=PIPE, encoding='utf8').stdout.split('\n')[0].split(' ')[-1].split('x')[::-1]]
        self.device_name = popen(r'.\Data\tools\adb -s {} shell getprop ro.product.model'.format(
            self.Eqlist.currentItem().text().split('\t')[0])).read().strip('\n')
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

        def Connect(port, host='127.0.0.1'):
            run([r'.\Data\tools\adb.exe', 'connect',
                 f'{host}:{port}'], stdout=PIPE)
        rhosts = con.get('Nox', 'rhost')
        lports = con.get('Nox', 'portlist')
        if lports:
            for port in eval(lports):
                t = threading.Thread(target=Connect, args=(port,), daemon=True)
                t.start()
            for l in run([r'.\Data\tools\adb', 'devices'], stdout=PIPE, encoding='utf8').stdout.rstrip('\n').split('\n'):
                if 'List' in l.split(' '):
                    continue
                if 'offline' in l:
                    continue
                b = l.split('\t')[0]
                if '127.0.0.1' in b:
                    eq_list.append(b+'\t模拟器')
                else:
                    eq_list.append(b+'\t手机')
            eq_list = list(set(eq_list))
            if not eq_list:
                self.setLog(self.tabname, logging.INFO,
                            self.Eqlist.objectName()+' 未检测到设备开启,请重新运行')
            else:
                self.Eqlist.addItems(eq_list)
        else:
            self.setLog(self.tabname, logging.WARNING, '本地未有设备(未扫描本地模拟器)')
        if rhosts:
            rports = con.get('Nox', 'rport')
            if rports:
                for port in eval(rports):
                    for host in eval(rhosts):
                        t = threading.Thread(
                            target=Connect, args=(port, host), daemon=True)
                        t.start()
                for l in run([r'.\Data\tools\adb', 'devices'], stdout=PIPE, encoding='utf8').stdout.rstrip('\n').split('\n'):
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
                eq_list = list(set(eq_list))
                if not eq_list:
                    self.setLog(self.tabname, logging.INFO,
                                self.Eqlist.objectName()+' 未检测到设备开启,请重新运行')
                else:
                    self.Eqlist.addItems(eq_list)
            else:
                self.setLog(self.tabname, logging.WARNING, '远程地址未有设备(未扫远程描模)')
                return
        self.setLog(self.tabname, logging.INFO,
                    self.Eqlist.objectName()+' 测试完成')

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
            shutil.copy('temp_Data\\three.png',
                        f'Data\\{self.tabname}_{self.running_mission}_{self.run_times}.png')

    def setLog(self, tabname, level, msg):
        logmsg = f'{logLevel[level]} {tabname}.{msg}'
        self.loger.log(level, f'{tabname}.{msg}')
        self.LogText.append(logmsg)


class MainWin(QMainWindow, Ui_MainWindow):
    """AutoArknights主界面"""

    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        QTextCodec.setCodecForLocale(QTextCodec.codecForName('utf8'))
        self.setupUi(self)
        self.p = Material.Penguin()
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
        self.login_ID.triggered.connect(self.login)
        self.add_plan.triggered.connect(self.append_plan)
        self.add_report.triggered.connect(self.append_report)
        self.plan.triggered.connect(self.run_plan)
        self.del_plan.triggered.connect(self.remove_plan)
        self.del_report.triggered.connect(self.remove_report)
        self.report.triggered.connect(self.run_report)

    def login(self):
        userid, ok = QInputDialog.getText(self, '请输入ID', '请输入登入ID')
        if ok:
            if not userid:
                QMessageBox.critical(self, '错误', '未输入ID')
                return
            self.p.update_id(userid)
            QMessageBox.information(self, '登入成功', '已登入ID:'+userid)

    def remove_report(self):
        while True:
            try:
                rrd = QDialog()
                rp = Rr_Dialog()
                rp.setupUi(rrd)
                ok = rrd.exec()
                if ok == QDialog.Accepted:
                    if not rp.items.currentItem():
                        self.p.remove_report(stage=rp.stage.text())
                        QMessageBox.information(self, '成功', '已删除选择关卡')
                        return
                    else:
                        self.p.remove_report()
                        self.p.remove_report(
                            itemid=rp.items.currentItem().text())
                        QMessageBox.information(
                            self, '成功', f'已删除{rp.items.currentItem().text()}')
                else:
                    break
            except AttributeError:
                QMessageBox.critical(self, '错误', '没有掉落物')
                return
            except FileNotFoundError:
                QMessageBox.critical(self, '错误', '未添加过数据')
                return

    def run_report(self):
        ask = QMessageBox(QMessageBox.Warning, '警告',
                          '<h1>请确认提交数据属实，否则可能会被判为异常处理</h1>', QMessageBox.Yes | QMessageBox.No)
        ok = ask.exec()
        if ok == QMessageBox.Yes:
            Hash = self.p.report()
            if 'userID' in Hash:
                QMessageBox.critical(self, '错误', '未登入ID')
                return
            if 'drops' in Hash:
                QMessageBox.critical(self, '错误', '未添加数据')
                return
            if Hash:
                QMessageBox.information(
                    self, '成功', '汇报成功,数据已清空\n汇报Hash已存放在Data\\report文件夹中，需要手动清理')
                with open(r'.\Data\report\{} report.txt'.format(strftime('%Y-%m-%d %H_%M_%S')), 'x', encoding='utf8') as f:
                    f.write(Hash)

    def remove_plan(self):
        while True:
            try:
                rpd = QDialog()
                name = Rp_Dialog()
                name.setupUi(rpd)
                ok = rpd.exec()
                if ok == QDialog.Accepted:
                    self.p.remove_need(name.names.currentItem().text())
                    QMessageBox.information(
                        self, '成功', f'已删除{name.names.currentItem().text()}')
                else:
                    break
            except AttributeError:
                QMessageBox.critical(self, '错误', '没有物品')
                return
            except FileNotFoundError:
                QMessageBox.critical(self, '错误', '未添加过数据')
                return

    def run_plan(self):
        od = QDialog()
        opt = PlanOption_Dialog()
        opt.setupUi(od)
        ok = od.exec()
        if ok == QDialog.Accepted:
            plan_result = self.p.plan(opt.extra.isChecked(
            ), opt.more_exp.isChecked(), opt.more_gold.isChecked())
            result = Material.Penguin.format_plan(plan_result)
            if not result:
                QMessageBox.warning(self, '无规划结果', '请检查是否添加数据')
                return
            with open('Data/plan/{} plan.txt'.format(strftime('%Y-%m-%d %H_%M_%S')), 'x', encoding='utf8') as f:
                f.write(result)
                QMessageBox.information(
                    self, '规划结果', result + '\n规划数据已清空\n规划结果已存放在Data\plan文件夹中,需要手动清理')

    def append_report(self):
        while True:
            rd = QDialog()
            stage = Report_Dialog()
            stage.setupUi(rd)
            ok = rd.exec()
            if ok == QDialog.Accepted:
                if not stage.drop_type.currentText() or not stage.item_name.currentText():
                    QMessageBox.warning(self, '错误', '未选择物品')
                    continue
                result = self.p.update_report(Material.Penguin.get_stageId_by_code(stage.stage.currentText()), Material.Penguin.droptype_to_EN(
                    stage.drop_type.currentText()), Material.Penguin.name_to_itemid(stage.item_name.currentText()), stage.item_quantity.value())
                if result:
                    QMessageBox.information(self, '添加成功', '添加成功')
                else:
                    QMessageBox.critical(self, '错误', '必须选择与上次一样的关卡')
            else:
                break

    def append_plan(self):
        temp = ''
        while True:
            pd = QDialog()
            item = Plan_Dialog()
            item.setupUi(pd)
            ok = pd.exec()
            if ok == QDialog.Accepted:
                self.p.update_need(item.item_name.currentText(),
                                   item.count.value())
                temp += '添加需求:{},数量:{}\n'.format(
                    item.item_name.currentText(), item.count.value())
            else:
                break
        QMessageBox.information(self, '添加成功', temp)

    def RS(self):
        lasthost = []
        lastport = []
        host, hok = QInputDialog.getText(
            self, '输入主机', '请输入主机名或IP地址\n127.0.0.1本地ip就不用输了,浪费性能和资源\n注意！如果配置文件中存在本地端口,则会使用本地端口进行测试,可能会造成检测不到!')
        if hok:
            if not host:
                QMessageBox.warning(self, '错误', '未输入主机名或IP地址')
                return
            else:
                if con.get('Nox', 'portlist'):
                    a = QMessageBox(QMessageBox.Question, '是否使用本地端口',
                                    '检测到本地存在模拟器\n是否用本地端口扫描远程端口?(这可能会导致扫描不到远程模拟器,因为端口原因,但是方便)', QMessageBox.Yes | QMessageBox.No)
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
                portList += [x[0] for x in re.findall('hostport="(\d*)" guestport="(\d*)"', open(
                    rf'{dir}\BignoxVMS\{file}\{file}.vbox', 'r').read())]
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
        作者CSDN：https://blog.csdn.net/qq_40173711''')

    def showSoft(self):
        QMessageBox.about(
            self, '关于软件', '版权所有CopyRight © 2020 Moran-Studio,basket_ball')

    def ScanEq(self):
        try:
            self.__listPort()
        except FileNotFoundError:
            QMessageBox.critical(self, '文件缺失', '缺少关键文件,请验证程序完整性')
        except:
            QMessageBox.warning(
                self, '模拟器不存在', '夜神模拟器不存在,在链接内刷新设备可连接手机/或点击远程扫描')

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
        app = QApplication(sys.argv)
        win = MainWin()
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched')
        if not os.path.exists('config.ini'):
            raise FileNotFoundError
        con = ConfigParser()
        con.read('config.ini', encoding='utf8')
        threading.Thread(target=win.show(), daemon=True).start()
        sys.exit(app.exec())
    except FileNotFoundError:
        QMessageBox.critical(win, '错误', '未找到config.ini\n请验证文件完整性')
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(2)
