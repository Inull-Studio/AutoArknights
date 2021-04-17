# coding:utf8
import requests
from PyQt5.QtGui import QGuiApplication
import json
import base64
import os
import urllib3

urllib3.disable_warnings()
DROP_TYPE = {'NORMAL_DROP': '常规掉落', 'EXTRA_DROP': '额外掉落',
             'SPECIAL_DROP': '特殊掉落', 'FURNITURE': '家具掉落'}


class Penguin(object):
    """企鹅统计相关api"""
    header = {'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.44 Safari/537.36 Edg/83.0.478.28',
              'accept': 'application/json, text/plain, */*', 'origin': 'https://penguin-stats.cn', }
    report_url = 'https://penguin-stats.cn/PenguinStats/api/v2/report'
    plan_url = 'https://planner.penguin-stats.io/plan'

    def __init__(self, uid=None):
        super(Penguin, self).__init__()
        self.cookies = {'userID': ''}
        self.required = {'exclude': [], "required": {}, "owned": {
        }, "extra_outc": False, "exp_demand": False, "gold_demand": False}
        self.report_json = {'server': 'CN', 'stageId': '', 'drops': []}

# 添加掉落汇报数据
    def update_report(self, stageId, drop_type, itemid, quantity):
        if self.report_json['stageId'] and stageId != self.report_json['stageId']:
            return None
        self.report_json['stageId'] = stageId
        self.header[
            'Referer'] = f'https://penguin-stats.cn/report/{Penguin.get_zoneId_by_stageId(stageId)}/{stageId}'
        self.report_json['drops'].append(
            {'dropType': drop_type, 'itemId': itemid, 'quantity': quantity})
        with open(r'.\temp_Data\report.txt', 'w', encoding='utf8') as f:
            f.write(str(self.report_json))
        return True

# 移除掉落汇报物品
    def remove_report(self, itemid: str = None, stage: str = None):
        if stage:
            self.report_json['stageId'] = ''
            self.header['Referer'] = ''
        for drop in self.report_json['drops']:
            if itemid == drop['itemId']:
                self.report_json['drops'].remove(drop)
                with open(r'.\temp_Data\report.txt', 'w', encoding='utf8') as f:
                    f.write(str(self.report_json))
                return True
        else:
            return None

# 汇报数据，返回哈希值
    def report(self):
        if not self.cookies['userID']:
            return 'no userID'
        if not self.report_json['drops']:
            return 'no drops'
        r = requests.post(
            self.report_url, json=self.report_json,
            headers=self.header, verify=False, cookies=self.cookies)
        if r.status_code == 201:
            self.report_json['drops'] = []
            self.report_json['stageId'] = ''
            os.remove(r'.\temp_Data\report.txt')
            return r.json()['reportHash']
        else:
            return None

# 上传企鹅统计ID
    def update_id(self, uid):
        self.cookies['userID'] = uid

# 删除企鹅统计ID
    def remove_id(self, uid):
        if uid == self.cookies['userID'] and self.cookies['userID']:
            self.cookies.pop('userID')
            return True
        else:
            return None

# 添加刷图规划材料
    def update_need(self, name: str, count: int):
        self.required['required'][name] = count
        with open(r'.\temp_Data\need.txt', 'w', encoding='utf8') as f:
            f.write(str(self.required))

# 移除刷图规划材料
    def remove_need(self, name: str):
        if name in self.required['required']:
            self.required['required'].pop(name)
            with open(r'.\temp_Data\need.txt', 'w', encoding='utf8') as f:
                f.write(str(self.required))
            return True
        else:
            return None

# 规划
    def plan(self, out: False, exp: False, gold: False):
        self.required['extra_outc'] = out
        self.required['exp_demand'] = exp
        self.required['gold_demand'] = gold
        if not self.required['required']:
            return None
        QGuiApplication.processEvents()
        r = requests.post(
            self.plan_url, json=self.required,
            headers=self.header, verify=False, cookies=self.cookies)
        if r.status_code == 200:
            self.required['required'] = {}
            os.remove(r'.\temp_Data\need.txt')
            return r.json()
        else:
            return None

# 格式化计划结果
    @staticmethod
    def format_plan(plan):
        if not plan:
            return None
        format_text = ''
        cost = str(plan['cost'])
        exp = str(plan['exp'])
        gold = str(plan['gold'])
        format_text += '预计理智花费: '+cost+'\n'
        format_text += '预计获得经验: '+exp+'\n'
        format_text += '预计龙门币收入: '+gold+'\n'
        stages = [
            '运行:'+' '+x['stage']+' ' + x['count']+' '+'次' for x in plan['stages']]
        synthesis = [
            '合成:'+' '+x['target']+' ' + x['count']+' '+'次' for x in plan['syntheses']]
        for stage in stages:
            format_text += stage+'\n'
        for synthesi in synthesis:
            format_text += synthesi+'\n'
        return format_text

# code转换zoneId
    @staticmethod
    def get_zoneId_by_code(code: str):
        data = Penguin.get_stage()
        return [x['zoneId'] for x in data if code == data['code']]

# stageID转换zoneId
    @staticmethod
    def get_zoneId_by_stageId(stageId: str):
        data = Penguin.get_stage()
        return [x['zoneId'] for x in data if stageId == x['stageId']][0]

# code转换stageId
    @staticmethod
    def get_stageId_by_code(code: str):
        data = Penguin.get_stage()
        return [x['stageId'] for x in data if code == x['code']][0]

# 获取当前刷图规划需求物品
    @staticmethod
    def get_need_names():
        with open(r'.\temp_Data\need.txt', 'r', encoding='utf8') as f:
            data = eval(f.read())
        return [x[0] for x in data['required'].items()]

# 获取当前掉落汇报的关卡
    @staticmethod
    def get_report_stage():
        with open(r'.\temp_Data\report.txt', 'r', encoding='utf8') as f:
            data = eval(f.read())
        return data['stageId']

# 获取当前掉落汇报的物品
    @staticmethod
    def get_report_items():
        with open(r'.\temp_Data\report.txt', 'r', encoding='utf8') as f:
            data = eval(f.read())
        return [x['itemId'] for x in data['drops']]

# 获取所有物品数据
    @ staticmethod
    def get_items():
        data = eval(open(r'.\Data\items.json', 'r', encoding='utf8').read())
        return data

# droptype英文转中文
    @ staticmethod
    def droptype_to_CN(dp: str):
        return DROP_TYPE[dp]

# droptype中文转英文
    @ staticmethod
    def droptype_to_EN(dp: str):
        return [x[0] for x in DROP_TYPE.items() if dp in x[1]][0]

# 物品id转换为物品名
    @ staticmethod
    def itemid_to_name(id: str):
        data = Penguin.get_items()
        item_name = [x['name'] for x in data if id in x.values()]
        if item_name:
            return item_name[0]

# 物品名转换为物品id
    @ staticmethod
    def name_to_itemid(name: str):
        data = Penguin.get_items()
        item_id = [x['itemId'] for x in data if name in x.values()]
        if item_id:
            return item_id[0]

# 获取关卡中掉落的物品id
    @ staticmethod
    def get_stage_itemId(stage: str):
        drop_infos = Penguin.get_dropinfos(stage)
        for x in drop_infos:
            item_id = [y['itemId'] for y in x if 'itemId' in y.keys()]
        return item_id

# 按照掉落类型获取关卡中掉落的物品id
    @ staticmethod
    def get_stage_itemId_by_droptype(stage: str, drop_type: str):
        drop_infos = Penguin.get_dropinfos(stage)
        for x in drop_infos:
            item_id = [
                y['itemId']for y in x if drop_type in y.values() and 'itemId' in y.keys()]
        return item_id

# 获取所有关卡掉落信息
    @ staticmethod
    def get_dropinfos(stage: str):
        data = Penguin.get_stage()
        drop_infos = [
            x['dropInfos']for x in data if 'dropInfos' in x.keys() and stage in x.values()]
        return drop_infos

# 获取关卡中所有掉落物品类型
    @staticmethod
    def get_droptype(stage: str):
        data = Penguin.get_dropinfos(stage)
        for x in data:
            drop_type = [y['dropType'] for y in x]
        if drop_type:
            return list(set(drop_type))
        else:
            return []

# 获取所有关卡code
    @staticmethod
    def get_stage_code():
        data = json.loads(
            open(r'.\Data\stage.json', 'r', encoding='utf8').read())
        return [x['code'] for x in data if 'dropInfos' in x.keys()]

# 获取所有关卡数据
    @staticmethod
    def get_stage(server: str = 'CN'):
        data = json.loads(
            open(r'.\Data\stage.json', 'r', encoding='utf8').read())
        return data

# 更新本地关卡信息
    @staticmethod
    def down_stage(server: str = 'CN'):
        r = requests.get(
            'https://penguin-stats.io/PenguinStats/api/v2/stages?server={server}')
        result = str(r.json())
        with open(r'.\Data\stage.json', 'w', encoding='utf8') as f:
            f.write(result)

# 更新本地物品信息
    @staticmethod
    def down_items():
        r = requests.get('https://penguin-stats.io/PenguinStats/api/v2/items')
        result = str(r.json())
        with open(r'.\Data\items.json', 'w', encoding='utf8') as f:
            f.write(result)
