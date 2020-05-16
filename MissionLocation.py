# coding:utf-8
from time import sleep
from subprocess import run, PIPE
import logging
from threading import Thread
from PyQt5.QtWidgets import QWidget
from os import system
import datetime
from cv2 import imread

logLevel = {10: 'DEBUG', 20: 'INFO',
            30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL'}


class M_to_L(object):
    def __init__(self, lizhi: dict, loger: logging.RootLogger, logText: QWidget, mission: str = '自己指定关卡'):
        self.mission = mission
        self.tap_str = 'adb -s {} shell input tap {} {}'
        self.lizhi = lizhi
        self.loger = loger
        self.logText = logText

    def selfMission(self, eq, size):
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return
        self.tap(eq, int(size[0]*(43/48)), int(size[1]*(11/12)))

    def sanxing(self, eq, size):
        system('adb -s '+eq+' shell screencap /sdcard/1.png')
        system('adb -s '+eq+' pull /sdcard/1.png Data\\three.png 1>nul 2>nul')
        system('adb -s '+eq+' shell rm /sdcard/1.png')
        data = imread('Data\\three.png')
        if data[int(size[1]*(51/72)), int(size[0]*(37/144))][2] == 62:
            system('del /q Data\\three.png')
            system(self.tap_str.format(eq, size[0]*0.75, size[1]*(2/9)))
            return 'Yes'
        elif data[int(size[1]*(51/72)), int(size[0]*(37/144))][2] == 74:
            system(self.tap_str.format(eq, size[0]*0.75, size[1]*(2/9)))
            system('del /q Data\\three.png')
            return 'No'
        else:
            system('del /q Data\\three.png')
            return 'False'

    def shengji(self, eq, size):
        sleep(1)
        system('adb -s '+eq+' shell screencap /sdcard/shengji.png')
        system('adb -s '+eq+' pull /sdcard/shengji.png Data\\shengji.png 1>nul 2>nul')
        system('adb -s '+eq+' shell rm /sdcard/shengji.png')
        data1 = imread('Data\\shengji.png')
        if data1[int(size[1]*0.4), int(size[0]*0.26875)][2] == 1:
            self.setLog(self.mission, logging.INFO, '发生升级')
            system(self.tap_str.format(eq, size[0]*0.75, size[1]*(2/9)))
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.3125)+' '+str(size[1]*(5/9)))
            sleep(5)
            return True
        else:
            return False

    def kaiqidaili(self, eq: str, size: list):
        self.setLog(self.mission, logging.INFO, '正在检测是否开启代理')
        sleep(1)
        system('adb -s '+eq+' shell screencap /sdcard/daili.png')
        system('adb -s '+eq+' pull /sdcard/daili.png Data\\daili.png >nul')
        system('adb -s '+eq+' shell rm /sdcard/daili.png')
        dailiImg = imread(r'Data\daili.png')
        if dailiImg[int(size[1]*(59/72)), int(size[0]*(123/144))][2] != 255:
            self.setLog(self.mission, logging.INFO, '未开启代理')
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.875)+' '+str(size[1]*0.85))
            self.setLog(self.mission, logging.INFO, '代理开启成功')
            system('del /s daili.png>nul')
            return True
        elif dailiImg[int(size[1]*(59/72)), int(size[0]*(123/144))][2] == 255:
            self.setLog(self.mission, logging.INFO, '代理已经开启')
            return True
        else:
            return False

    def checklizhi(self, eq: str, size: list):
        self.setLog(self.mission, logging.INFO, '正在检测理智')
        sleep(0.5)
        system('adb -s '+eq+' shell screencap /sdcard/lizhi.png')
        system('adb -s '+eq+' pull /sdcard/lizhi.png Data\\lizhi.png 1>nul 2>nul')
        system('adb -s '+eq+' shell rm /sdcard/lizhi.png')
        lizhiImg = imread('Data\\lizhi.png')
        if lizhiImg[int(size[1]*(5/9)), int(size[0]*(120/144))][2] != 130:
            if self.lizhi['buhuifu']:
                return 'buhuifu'
            else:
                if lizhiImg[int(size[1]*(5/36)), int(size[0]*(75/144))][2] == 255 and self.lizhi['yaoji']:
                    system('adb -s '+eq+' shell input tap ' +
                           str(size[0]*0.85625)+' '+str(size[1]*(34/45)))
                    sleep(1)
                    system('adb -s '+eq+' shell input tap ' +
                           str(size[0]*0.875)+' '+str(size[1]*(8/9)))
                    sleep(2)
                    return False
                elif lizhiImg[int(size[1]*(5/36)), int(size[0]*(106/144))][2] == 255 and self.lizhi['yaoji']:
                    self.setLog(self.mission, logging.WARN, '没有药剂，无法恢复，终止程序')
                    sleep(1)
                    return True
                elif self.lizhi['yuanshi']:
                    system('adb -s '+eq+' shell input tap ' +
                           str(size[0]*0.85625)+' '+str(size[1]*(34/45)))
                    system('adb -s '+eq+' shell screencap /sdcard/2.png')
                    system('adb -s '+eq +
                           ' pull /sdcard/2.png Data\\2.png 1>nul 2>nul')
                    system('adb -s '+eq+' shell rm /sdcard/2.png')
                    sleep(1)
                    shitou = imread('Data\\2.png')
                    if shitou[int(size[1]*(7/45)), int(size[0]*0.275)][2] == 255:
                        return False
                    return True
        else:
            self.setLog(self.mission, logging.INFO, '有理智')
            return False

    def retMission(self):
        if 'AP' in self.mission:
            if '5' in self.mission:
                return self.AP5
            elif '4' in self.mission:
                return self.AP4
            elif '3' in self.mission:
                return self.AP3
            elif '2' in self.mission:
                return self.AP2
            else:
                return self.AP1
        elif 'CA' in self.mission:
            if '5' in self.mission:
                return self.LS5
            elif '4' in self.mission:
                return self.LS4
            elif '3' in self.mission:
                return self.LS3
            elif '2' in self.mission:
                return self.LS2
            else:
                return self.LS1
        elif 'CE' in self.mission:
            if '5' in self.mission:
                return self.LS5
            elif '4' in self.mission:
                return self.LS4
            elif '3' in self.mission:
                return self.LS3
            elif '2' in self.mission:
                return self.LS2
            else:
                return self.LS1
        elif 'LS' in self.mission:
            if '5' in self.mission:
                return self.LS5
            elif '4' in self.mission:
                return self.LS4
            elif '3' in self.mission:
                return self.LS3
            elif '2' in self.mission:
                return self.LS2
            else:
                return self.LS1
        elif 'SK' in self.mission:
            if '5' in self.mission:
                return self.SK5
            elif '4' in self.mission:
                return self.SK4
            elif '3' in self.mission:
                return self.SK3
            elif '2' in self.mission:
                return self.SK2
            else:
                return self.SK1

    def AP(self, eq: str, size: list):
        now = (datetime.datetime.now() -
               datetime.timedelta(hours=4)).strftime('%A')
        size = [int(x) for x in size]
        if now == 'Monday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))
            sleep(0.5)
        elif now == 'Tuesday':
            print('今天是星期二,今天没有凭证')
        elif now == 'Wednesday':
            print('今天是星期三,今天没有凭证')
        elif now == 'Thursday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))
            sleep(0.5)
        elif now == 'Firday':
            prnt('今天是星期五,今天没有凭证')
        elif now == 'Saturday':
            system(self.tap_str.format(eq, size[0]*0.75, size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))
            sleep(0.5)
        elif now == 'Sunday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))

    def CA(self, eq: str, size: list):
        now = (datetime.datetime.now() -
               datetime.timedelta(hours=4)).strftime('%A')
        size = [int(x) for x in size]
        if now == 'Saturday':
            return None
        elif now == 'Monday':
            print('今天是星期一')
        elif now == 'Tuesday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq + ' shell input tap ' +
                   str(size[0]*0.375)+' '+str(size[1]*(5/9)))
            sleep(0.5)
        elif now == 'Wednesday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq + ' shell input tap ' +
                   str(size[0]*0.375)+' '+str(size[1]*(5/9)))
            sleep(0.5)
        elif now == 'Thursday':
            print('今天是星期四,今天没有技能书')
        elif now == 'Firday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))
            sleep(0.5)
        elif now == 'Sunday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.34375)+' '+str(size[1]*0.5))
            sleep(0.5)

    def CE(self, eq: str, size: list):
        now = (datetime.datetime.now() -
               datetime.timedelta(hours=4)).strftime('%A')
        size = [int(x) for x in size]
        if now == 'Monday':
            return None
        elif now == 'Tuesday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.5625)+' '+str(size[1]*(5/9)))
            sleep(0.5)
        elif now == 'Wednesday':
            return None
        elif now == 'Thursday':
            system(f'adb -s {eq} shell input tap {size[0]*0.75} {size[1]*(2/9)}')
            sleep(0.5)
            system(f'adb -s {eq} shell input tap {size[0]*0.1875} {size[1]*(83/90)}')
            sleep(0.5)
            system(f'adb -s {eq} shell input tap {size[0]*0.5625} {size[1]*(5/9)}')
            sleep(0.5)
        elif now == 'Friday':
            return None
        elif now == 'Saturday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(4/9)))
            sleep(0.5)
        elif now == 'Sunday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(5/9)))
            sleep(0.5)

    def LS(self, eq: str, size: list):
        system(self.tap_str.format(eq, size[0]*0.75, size[1]*(2/9)))
        sleep(0.5)
        system(self.tap_str.format(eq, size[0]*0.1875, size[1]*(83/90)))
        sleep(0.5)
        system(self.tap_str.format(eq, size[0]*0.125, size[1]*(4/9)))
        sleep(0.5)

    def SK(self, eq: str, size: list):
        if now == 'Monday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.5625)+' '+str(size[1]*(5/9)))
            sleep(0.5)
        elif now == 'Tuesday':
            print('今天是星期二,今天没有')
        elif now == 'Wednesday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.5625)+' '+str(size[1]*(5/9)))
        elif now == 'Thursday':
            print('今天是星期四,今天没有')
        elif now == 'Friday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.5625)+' '+str(size[1]*(5/9)))
            sleep(0.5)
        elif now == 'Saturday':
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.75)+' '+str(size[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(size[0]*0.1875)+' '+str(size[1]*(8/9)))
            sleep(0.5)
            self.tap(eq, int(size[0]*0.5625), int(size[1]*0.3125))
            sleep(0.5)
        elif now == 'Sunday':
            print('今天是星期日,今天没有')

    def tap(self, eq: str, x: int, y: int):
        run(['adb', '-s', eq, 'shell', 'input', 'tap', str(x), str(y)], stdout=PIPE)

    def AP1(self, eq, size):
        self.AP(eq, size)
        system(self.tap_str.format(eq, size[0]*5/24, size[1]*(57/72)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def AP2(self, eq, size):
        self.AP(eq, size)
        self.tap(eq, size[0]*(55/144), size[1]*(13/18))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def AP3(self, eq, size):
        self.AP(eq, size)
        self.tap(eq, size[0]*(19/36), size[1]*(41/72))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def AP4(self, eq, size):
        self.AP(eq, size)
        system(self.tap_str.format(eq, size[0]*(47/72), size[1]*(5/12)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def AP5(self, eq, size):
        self.AP(eq, size)
        system(self.tap_str.format(eq, size[0]*0.74375, size[1]*(43/180)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def CE1(self, eq, size):
        self.CE(eq, size)
        system(self.tap_str.format(eq, size[0]*5/24, size[1]*(57/72)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def CE2(self, eq, size):
        self.CE(eq, size)
        self.tap(eq, size[0]*(55/144), size[1]*(13/18))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def CE3(self, eq, size):
        self.CE(eq, size)
        self.tap(eq, size[0]*(19/36), size[1]*(41/72))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def CE4(self, eq, size):
        self.CE(eq, size)
        system(self.tap_str.format(eq, size[0]*(47/72), size[1]*(5/12)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def CE5(self, eq, size):
        self.CE(eq, size)
        system(self.tap_str.format(eq, size[0]*0.74375, size[1]*(43/180)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def SK1(self, eq, size):
        self.SK(eq, size)
        self.tap(eq, size[0]*5/24, size[1]*(57/72))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def SK2(self, eq, size):
        self.SK(eq, size)
        self.tap(eq, size[0]*(55/144), size[1]*(13/18))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def SK3(self, eq, size):
        self.SK(eq, size)
        self.tap(eq, size[0]*(19/36), size[1]*(41/72))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def SK4(self, eq, size):
        self.SK(eq, size)
        system(self.tap_str.format(eq, size[0]*(47/72), size[1]*(5/12)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def SK5(self, eq, size):
        self.SK(eq, size)
        system(self.tap_str.format(eq, size[0]*0.74375, size[1]*(43/180)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def LS1(self, eq, size):
        self.LS(eq, size)
        system('adb -s '+eq+' shell input tap ' +
               str(size[0]*(5/24))+' '+str(size[1]*(57/72)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def LS2(self, eq, size):
        self.LS(eq, size)
        system('adb -s '+eq+' shell input tap ' +
               str(size[0]*(13/36))+' '+str(size[1]*(29/36)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def LS3(self, eq, size):
        self.LS(eq, size)
        system('adb -s '+eq+' shell input tap ' +
               str(size[0]*(19/36))+' '+str(size[1]*(5/14)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def LS4(self, eq, size):
        self.LS(eq, size)
        system('adb -s '+eq+' shell input tap ' +
               str(size[0]*(47/72))+' '+str(size[1]*(5/12)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return

    def LS5(self, eq, size):
        self.LS(eq, size)
        system('adb -s '+eq+' shell input tap ' +
               str(size[0]*0.74375)+' '+str(size[1]*(43/180)))
        if not self.kaiqidaili(eq, size):
            self.setLog(self.mission, logging.WARN, '代理开启失败')
            return
        system(self.tap_str.format(eq, size[0]*0.875, size[1]*(8/9)))

    def setLog(self, mission, level, msg):
        logmsg = f'{logLevel[level]} {mission}.{msg}'
        self.loger.log(level, f'{mission}.{msg}')
        self.logText.append(logmsg)


if __name__ == '__main__':
    Mission = M_to_L('CE-5')
    func = Mission.retMission()
    func('LS-5', [1600, 900])
