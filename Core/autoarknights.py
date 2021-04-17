try:
    import cv2
except ImportError as e:
    from os import popen
    print('未安装对应库，正在自动安装')
    popen('pip3 insatll -r r.txt').read()
    print('请重新运行')
    sys.exit(3)
else:
    import sys
    import os
    import re
    import threading
    from os import system, popen, walk, listdir
    from time import sleep, localtime, strftime
    from cv2 import imread


def listPort(dir):
    global ports
    if not os.path.exists('ports'):
        portList = []
        for file in listdir(rf'{dir}\BignoxVMS'):
            portList += [x[0] for x in re.findall('hostport="(.*)" guestport="(\d*)"', open(rf'{dir}\BignoxVMS\{file}\{file}.vbox', 'r').read())]
        portList = list(set(portList))
        open('ports', 'w').write(repr(portList).strip('[]').replace('\'', ''))
        return portList
    else:
        portList = open(os.path.realpath('')+'\\ports',
                        'r').read().replace(' ', '').split(',')
        os.chdir('..')
        return portList


def checkVMSdir(drivers):
    global ports
    os.chdir(os.path.realpath('data'))
    if not os.path.exists('Noxfile'):
        for driver in drivers:
            for root, dirs, files in walk(driver):
                if 'BignoxVMS' in dirs:
                    print(('已检测到存在夜神模拟器\t'+root))
                    open('Noxfile', 'w').write(root)
                    sleep(1)
                    listPort(root)
        print('无夜神模拟器,请重试')
        sys.exit(2)
    else:
        if os.path.exists('Noxfile'):
            print('已检测到存在夜神模拟器')
            sleep(1)
            return open(os.path.realpath('')+'\\Noxfile', 'r').read()


def checklizhi():
    global eq, yaoji, lizhihuifu, sizeList
    print('正在检测理智')
    lizhi = True
    while lizhi:
        sleep(0.5)
        system('adb -s '+eq+' shell screencap /sdcard/lizhi.png')
        system('adb -s '+eq+' pull /sdcard/lizhi.png lizhi.png >nul')
        system('adb -s '+eq+' shell rm /sdcard/lizhi.png')
        lizhiImg = imread('lizhi.png')
        sleep(0.5)
        if lizhiImg[600, 1500][2] == 252:
            print('没有理智，正在检测是否继续运行')
            if lizhihuifu:
                if lizhiImg[100, 1110][2] == 255 and yaoji:
                    system('adb -s '+eq+' shell input tap ' +
                           str(sizeList[0]*0.85625)+' '+str(sizeList[1]*(34/45)))
                    print('继续执行')
                    sleep(1)
                    system('adb -s '+eq+' shell input tap ' +
                           str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
                    sleep(2)
                    return False
                elif lizhiImg[1220, 100][2] == 84 and yaoji:
                    print('没有药剂，无法恢复，终止程序')
                    sleep(1)
                    return True
                elif not yaoji:
                    system('adb -s '+eq+' shell input tap ' +
                           str(sizeList[0]*0.85625)+' '+str(sizeList[1]*(34/45)))
                    system('adb -s '+eq+' shell screencap /sdcard/2.png')
                    system('adb -s '+eq+' pull /sdcard/2.png 2.png >nul')
                    system('adb -s '+eq+' shell rm /sdcard/2.png')
                    sleep(1)
                    shitou = imread('2.png')
                    if shitou[670, 470][2] == 149:
                        print('没有石头，无法购买，终止程序')
                        sleep(1)
                        return True
                    return False
            else:
                print('结束执行')
                sleep(2)
                return True
        else:
            print('有理智，继续运行')
            break


def kaiqidaili():
    global eq, sizeList
    print('正在检测是否开启代理')
    dailizhuangtai = True
    while dailizhuangtai:
        sleep(1)
        system('adb -s '+eq+' shell screencap /sdcard/daili.png')
        system('adb -s '+eq+' pull /sdcard/daili.png daili.jpg >nul')
        system('adb -s '+eq+' shell rm /sdcard/daili.png')
        dailiImg = imread('daili.jpg')
        if dailiImg[735, 1385][2] == 28:
            print('未开启代理')
            print('正在开启代理')
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*0.85))
            print('代理开启成功')
            system('del /s daili.png>nul')
            break
        elif dailiImg[735, 1385][2] == 164:
            print('代理已经开启')
            sleep(1)
            break
        else:
            continue

class wuzichoubei:
    def ls4(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.625)+' '+str(sizeList[1]*(35/90)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def ls5(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.74375)+' '+str(sizeList[1]*(43/180)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def ce4(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.625)+' '+str(sizeList[1]*(35/90)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def ce5(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +
               str(sizeList[0]*0.73125)+' '+str(sizeList[1]*(11/45)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def ap3(self):
        pass

    def ap1(self):
        pass

    def ca1(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +
               str(sizeList[0]*0.15625)+' '+str(sizeList[1]*(7/9)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def ca2(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+'shell input tap ' +str(sizeList[0]*0.375)+' '+str(sizeList[1]*(13/18)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            system('cls')

    def sk4(self):
        global stars, pdup, shiwu, eq, sizeList
        system('adb -s '+eq+' shell input tap ' +
               str(sizeList[0]*0.625)+' '+str(sizeList[1]*(7/18)))
        sleep(0.5)
        kaiqidaili()
        threestars = True
        while threestars:
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            if checklizhi():
                break
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.875)+' '+str(sizeList[1]*(8/9)))
            sleep(60)
            stars = True
            pdup = True
            shiwu = True
            while stars and shiwu and pdup:
                dailishiwu()
                sanxing()
                shengji()
            sleep(1)
            system('cls')


def error(errornum):
    if errornum == 1:
        print('发生错误\n请检查模拟器是否开启\n手机是否连接\n或清除端口缓存再重试一次')
        sys.exit(1)


def apxingqi():
    global eq, ports, sizeList
    now = strftime('%A', localtime())
    eq_list = []
    print('正在测试手机连接')
    errornum = system('adb tcpip 5555>nul')
    if len(ports):
        print('正在测试模拟器端口\n')
        for port in ports:
            errornum = system(f'adb connect 127.0.0.1:{port}>nul')
        error(errornum)
    if popen(r"for /f 'usebackq' %i in (`adb devices`) do set /a a+=1").readlines()[-1] >= '2':
        for l in popen('adb devices').readlines():
            if l.split(' ')[0] == 'List':
                continue
            if l == '\n':
                continue
            print(('设备:\t'+l.split('\t')[0]))
            b = l.split('\t')[0]
            eq_list.append(b)
        eq = eval(input('请输入要打开的设备:'))
        if eq in eq_list:
            sizeList = [int(x) for x in popen('adb -s '+eq+' shell wm size').readlines()[0].split(' ')[-1].split('\n')[0].split('x')]
            if now == 'Saturday':
                print('今天是星期六')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
            elif now == 'Firday':
                prnt('今天是星期五,今天没有凭证')
            elif now == 'Thursday':
                print('今天是星期四')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
            elif now == 'Wednesday':
                print('今天是星期三,今天没有凭证')
            elif now == 'Tuesday':
                print('今天是星期二,今天没有凭证')
            elif now == 'Monday':
                print('今天是星期一')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
            elif now == 'Sunday':
                print('今天是星期日')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
        else:
            print('请输入正确的格式')
            sys.exit(1)


def caxingqi():
    global eq, ports, sizeList
    now = strftime('%A', localtime())
    eq_list = []
    print('正在测试手机连接')
    errornum = system('adb tcpip 5555>nul')
    if len(ports):
        print('正在测试模拟器端口\n')
        for port in ports:
            errornum = system(f'adb connect 127.0.0.1:{port}>nul')
        error(errornum)
    if popen(r"for /f 'usebackq' %i in (`adb devices`) do set /a a+=1").readlines()[-1] >= '2':
        for l in popen('adb devices').readlines():
            if l.split(' ')[0] == 'List':
                continue
            if l == '\n':
                continue
            print(('设备:\t'+l.split('\t')[0]))
            b = l.split('\t')[0]
            eq_list.append(b)
        eq = eval(input('请输入要打开的设备:'))
        if eq in eq_list:
            sizeList = [int(x) for x in popen(
                'adb -s '+eq+' shell wm size').readlines()[0].split(' ')[-1].split('\n')[0].split('x')]
            if now == 'Saturday':
                print('今天是星期六,今天没有技能书')
                sys.exit(0)
            elif now == 'Monday':
                print('今天是星期一')
            elif now == 'Tuesday':
                print('今天是星期二')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq + ' shell input tap ' +
                       str(sizeList[0]*0.375)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Wednesday':
                print('今天是星期三')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq +' shell input tap '+str(sizeList[0]*0.375)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Thursday':
                print('今天是星期四,今天没有技能书')
            elif now == 'Firday':
                print('今天是星期五,今天没有技能书')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
            elif now == 'Sunday':
                print('今天是星期日')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.34375)+' '+str(sizeList[1]*0.5))
                sleep(0.5)
        else:
            print('请输入正确的格式')
            sys.exit(1)


def lsxingqi():
    global eq, ports, sizeList
    eq_list = []
    print('正在测试手机连接')
    errornum = system('adb tcpip 5555>nul')
    if len(ports):
        print('正在测试模拟器端口\n')
        for port in ports:
            errornum = system(f'adb connect 127.0.0.1:{port}>nul')
        error(errornum)
    if popen(r"for /f 'usebackq' %i in (`adb devices`) do set /a a+=1").readlines()[-1] >= '2':
        for l in popen('adb devices').readlines():
            if l.split(' ')[0] == 'List':
                continue
            if l == '\n':
                continue
            print(('设备:\t'+l.split('\t')[0]))
            b = l.split('\t')[0]
            eq_list.append(b)
        eq = eval(input('请输入要打开的设备:'))
        if eq in eq_list:
            print(('今天是'+strftime('%A', localtime())))
            sizeList = [int(x) for x in popen(
                'adb -s '+eq+' shell wm size').readlines()[0].split(' ')[-1].split('\n')[0].split('x')]
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
            sleep(0.5)
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.125)+' '+str(sizeList[1]*(4/9)))
            sleep(0.5)
        else:
            print('请输入正确的格式')
            sys.exit(1)


def cexingqi():
    global eq, ports, sizeList
    now = strftime('%A', localtime())
    eq_list = []
    print('正在测试手机连接')
    errornum = system('adb tcpip 5555>nul')
    if len(ports):
        print('正在测试模拟器端口\n')
        for port in ports:
            errornum = system(f'adb connect 127.0.0.1:{port}>nul')
        error(errornum)
    if popen(r"for /f 'usebackq' %i in (`adb devices`) do set /a a+=1").readlines()[-1] >= '2':
        for l in popen('adb devices').readlines():
            if l.split(' ')[0] == 'List':
                continue
            if l == '\n':
                continue
            print(('设备:\t'+l.split('\t')[0]))
            b = l.split('\t')[0]
            eq_list.append(b)
        eq = eval(input('请输入要打开的设备:'))
        if eq in eq_list:
            sizeList = [int(x) for x in popen('adb -s '+eq+' shell wm size').readlines()[0].split(' ')[-1].split('\n')[0].split('x')]
            if now == 'Saturday':
                print('今天是星期六')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(4/9)))
                sleep(0.5)
            elif now == 'Monday':
                print('今天是星期一,今天没有龙门币')
                sys.exit(0)
            elif now == 'Tuesday':
                print('今天是星期二')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Thursday':
                print('今天是星期三,今天没有龙门币')
            elif now == 'Thursday':
                print('今天是星期四')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Firday':
                print('今天是星期五,今天没有龙门币')
                sys.exit(0)
            elif now == 'Sunday':
                print('今天是星期日')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
        else:
            print('请输入正确的格式')
            sys.exit(1)


def skxingqi():
    global eq, ports, sizeList
    now = strftime('%A', localtime())
    eq_list = []
    print('正在测试手机连接')
    errornum = system('adb tcpip 5555>nul')
    if len(ports):
        print('正在测试模拟器端口\n')
        for port in ports:
            errornum = system(f'adb connect 127.0.0.1:{port}>nul')
        error(errornum)
    if popen(r"for /f 'usebackq' %i in (`adb devices`) do set /a a+=1").readlines()[-1] >= '2':
        for l in popen('adb devices').readlines():
            if l.split(' ')[0] == 'List':
                continue
            if l == '\n':
                continue
            print(('设备:\t'+l.split('\t')[0]))
            b = l.split('\t')[0]
            eq_list.append(b)
        eq = eval(input('请输入要打开的设备:'))
        if eq in eq_list:
            sizeList = [int(x) for x in popen(
                'adb -s '+eq+' shell wm size').readlines()[0].split(' ')[-1].split('\n')[0].split('x')]
            if now == 'Saturday':
                print('今天是星期六')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(8/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*0.3125))
                sleep(0.5)
            elif now == 'Monday':
                print('今天是星期一')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Tuesday':
                print('今天是星期二,今天没有')
            elif now == 'Wednesday':
                print('今天是星期三')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*(5/9)))
            elif now == 'Thursday':
                print('今天是星期四,今天没有')
            elif now == 'Friday':
                print('今天是星期五')
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.1875)+' '+str(sizeList[1]*(83/90)))
                sleep(0.5)
                system('adb -s '+eq+' shell input tap ' +
                       str(sizeList[0]*0.5625)+' '+str(sizeList[1]*(5/9)))
                sleep(0.5)
            elif now == 'Sunday':
                print('今天是星期日,今天没有')
        else:
            print('请输入正确的格式')
            sys.exit(1)


def dailishiwu():
    global eq, shiwu, sizeList
    while shiwu:
        print('正在检测代理失误')
        system('adb -s '+eq+' shell screencap /sdcard/shiwu.png')
        system('adb -s '+eq+' pull /sdcard/shiwu.png shiwu.png >nul')
        system('adb -s '+eq+' shell rm /sdcard/shiwu.png')
        data2 = imread('shiwu.png')
        if data2[630, 1300][2] == 115:
            print('发生代理失误')
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/3)))
            shiwu = False
            break
        else:
            print('无代理失误')
            break


def shengji():
    global eq, pdup, sizeList
    while pdup:
        print('正在检测升级')
        sleep(1)
        system('adb -s '+eq+' shell screencap /sdcard/shengji.png')
        system('adb -s '+eq+' pull /sdcard/shengji.png shengji.png >nul')
        system('adb -s '+eq+' shell rm /sdcard/shengji.png')
        data1 = imread('shengji.png')
        if data1[630, 430][2] == 1:
            print('发生升级')
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
            pdup = False
            system('del /q shengji.png')
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.3125)+' '+str(sizeList[1]*(5/9)))
            sleep(5)
            break
        else:
            print('无升级')
            break


def sanxing():
    sanxing_times = 0
    global eq, stars, sizeList
    while stars:
        print('正在检测三星')
        system('adb -s '+eq+' shell screencap /sdcard/1.png')
        system('adb -s '+eq+' pull /sdcard/1.png 1.png >nul')
        system('adb -s '+eq+' shell rm /sdcard/1.png')
        data = imread('1.png')
        if data[660, 465][2] == 63:
            print('OK')
            system('adb -s '+eq+' shell input tap ' +
                   str(sizeList[0]*0.75)+' '+str(sizeList[1]*(2/9)))
            stars = False
            system('del /q 1.png')
            sleep(8)
            break
        elif data[660, 465][0] == 86:
            print('发生失误，不是三星')
            if sanxing_times == 1:
                threestars = False
                print('不是三星，程序继续运行')
                break
            print('重新检测')
            sanxing_times += 1
            continue
        else:
            print('正在重复检测三星')
            break


if __name__ == '__main__':
    global ports, lizhihuifu, yaoji
    print('正在检测夜神模拟器(第一次时间稍长，请耐心等待)')
    ports = listPort(checkVMSdir(re.sub('\n', '', popen(
        'fsutil fsinfo drives').read()).split(' ')[1:-1]))
    while True:
        system('cls')
        mission = input(
            '请输入关卡号(输入n退出,输入help查看当前存在关卡,输入lizhi更改没有理智时的操作)：').strip().lower()
        if mission == 'lizhi':
            lizhihuifu = False
            while True:
                f = input('没有理智时是否自动购买理智(Y/N)').lower()
                if f == 'y':
                    f = input('要使用药剂恢复还是用至纯原石恢复?(Y/N)').lower()
                    if f == 'y':
                        f = input('确定吗?(Y/N)').lower()
                        if f == 'y':
                            yaoji = True
                            lizhihuifu = True
                            print('药剂恢复')
                            sleep(0.5)
                            break
                        elif f == 'n':
                            lizhihuifu = True
                            yaoji = False
                            print('至纯原石恢复')
                            sleep(0.5)
                            break
                        else:
                            print('格式输入错误,请重新输入')
                            sleep(1)
                            system('cls')
                    elif f == 'n':
                        f = input('确定吗?(Y/N)').lower()
                        if f == 'y':
                            yaoji = True
                            lizhihuifu = False
                            print('至纯原石恢复')
                            sleep(0.5)
                            break
                        elif f == 'n':
                            lizhihuifu = True
                            yaoji = True
                            print('药剂恢复')
                            sleep(0.5)
                            break
                        else:
                            print('格式输入错误,请重新输入')
                            sleep(1)
                            system('cls')
                    else:
                        print('格式输入错误,请重新输入')
                        sleep(1)
                        system('cls')
                elif f == 'n':
                    print('不恢复理智')
                    lizhihuifu = False
                    sleep(1)
                    break
                else:
                    print('格式输入错误,请重新输入')
                    sleep(1)
                    system('cls')
        elif mission == 'n':
            mission = ''
            print('再见')
            sleep(1)
            sys.exit(0)
        elif mission == 'ls4':
            mission = ''
            lsxingqi()
            t = zhanshuyanxi()
            t.ls4()
        elif mission == 'ls5':
            mission = ''
            lsxingqi()
            t = zhanshuyanxi()
            t.ls5()
        elif mission == 'ce4':
            mission = ''
            cexingqi()
            t = zhanshuyanxi()
            t.ce4()
        elif mission == 'ca1':
            mission = ''
            caxingqi()
            t = zhanshuyanxi()
            t.ca1()
        elif mission == 'ca2':
            mission = ''
            caxingqi()
            t = zhanshuyanxi()
            t.ca2()
        elif mission == 'ce5':
            mission = ''
            cexingqi()
            t = zhanshuyanxi()
            t.ce5()
        elif mission == 'ap3':
            mission = ''
            apxingqi()
            t = zhanshuyanxi()
            t.ap3()
        elif mission == 'sk4':
            mission = ''
            skxingqi()
            t = zhanshuyanxi()
            t.sk4()
        elif mission == 'help':
            mission = ''
            for a in dir(zhanshuyanxi):
                b = re.match('[0-9a-zA-Z]', a)
                if b:
                    print((b.string))
                else:
                    continue
            system('pause')
        else:
            system('cls')
            print('请输入正确的格式(详情请看帮助help)')
            sleep(1)
