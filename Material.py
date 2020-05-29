import requests,json
import urllib3

urllib3.disable_warnings()


class Penguin(object):
    """docstring for Penguin"""
    header = {
        'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.44 Safari/537.36 Edg/83.0.478.28',
        'accept': 'application/json, text/plain, */*',
        'origin': 'https://penguin-stats.cn',
    }
    report_url = 'https://penguin-stats.cn/PenguinStats/api/v2/report'
    plan_url = 'https://planner.penguin-stats.io/plan'
    ocr_url='https://api.ocr.space/parse/image'
    Key='d2a5ef2f7188957'


    def __init__(self, uid=None):
        super(Penguin, self).__init__()
        self.cookies = {}
        self.required = {
            'exclude': [],
            "required": {},
            "owned": {},
            "extra_outc": 'false',
            "exp_demand": 'false',
            "gold_demand": 'false'
        }
        self.report_json = {
            'server': 'CN',
            'stageId': '',
            'drops': []
        }

    def update_report(self, stageId, drop_type, itemid, quantity):
        self.report_json['stageId'] = stageId
        self.report_json['drops'].append(
            {
                'dropType': drop_type,
                'itemId': itemid,
                'quantity': quantity
            }
        )

    def report(self):
        '''汇报数据
        返回结果 哈希值'''
        r = requests.post(self.report_url, json=self.report_json,
                          headers=self.header, verify=False, cookies=self.cookies)
        print(r.status_code)
        # if r.status_code==201:
        return r.json()['reportHash']
        # else:
        #     print('汇报出错')

    def ocr(self,file):
        pass

    def update_id(self, uid):
        self.cookies['userID'] = uid

    def remove_id(self,uid):
        if uid==self.cookies['userID']:
            self.cookies['userID']==None
    def update_need(self, name: str, count: int):
        print('添加需求:{},数量:{}'.format(name, count))
        self.required['required'][name] = count

    def remove_need(self, name: str):
        if name in self.required['required']:
            self.required['required'].pop(name)

    def plan(self):
        r = requests.post(self.plan_url, json=self.required,
                          headers=self.header, verify=False, cookies=self.cookies)
        if r.status_code == 200:
            return r.json()
        else:
            print('计划出错')
    @staticmethod
    def get_all_items():
        r=requests.get('https://penguin-stats.io/PenguinStats/api/v2/items')
        result=str(r.json())
        with open('.Data\\items.json','w',encoding='utf8') as f:
            f.write(result)



if __name__ == '__main__':
    p = Penguin()
    # p.update_need('提纯源岩', 8)
    # p.update_id('66068307')
    # p.update_report('pro_a_2', 'SPECIAL_DROP', 'ap_supply_lt_010',1)
    # print(p.report(),'\n')
    # data = p.plan()
    # print('预计理智花费:', data['cost'])
    # print('预计获得经验:', data['exp'])
    # print('预计龙门币收入:', data['gold'])
    # print()
    # [print('运行关卡:', x['stage'], x['count'], '次') for x in data['stages']]
    # print()
    # [print('合成:', x['target'], x['count'], '次') for x in data['syntheses']]
