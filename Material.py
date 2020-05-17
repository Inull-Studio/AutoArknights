import requests
import urllib3
import cv2
import numpy as np

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
            'source': 'frontend-v2',
            'stageId': '',
            'version': 'v3.0.1',
            'drops': []
        }

    def update_report(self, stageId, drop_type, itemid, quantity):
        self.report_json['drops'].append(
            {
                'dropType': drop_type,
                'itemId': itemid,
                'quantity': quantity
            }
        )
        self.report_json['stageId'] = stageId

    def report(self):
        r = requests.post(self.report_url, json=self.report_json,
                          headers=self.header, verify=False, cookies=self.cookies)

    def update_id(self, uid):
        self.cookies['userID'] = uid

    def update_need(self, name: str, count: int):
        self.required['required'][name] = count

    def remove_need(self, name: str):
        if name in self.required['required']:
            self.required['required'].pop(name)
        else:
            pass

    def plan(self):
        r = requests.post(self.plan_url, json=self.required,
                          headers=self.header, verify=False, cookies=self.cookies)
        if r.status_code == 200:
            planner = r.json()
            return planner
        else:
            pass


if __name__ == '__main__':
    p = Penguin()
    p.update_need('提纯源岩', 8)
    p.update_id('66068307')
    data = p.plan()
    print('预计理智花费:', data['cost'])
    print('预计获得经验:', data['exp'])
    print('预计龙门币收入:', data['gold'])
    print()
    [print('关卡:', x['stage'], x['count'], '次') for x in data['stages']]
    print()
    [print('合成:', x['target'], x['count'], '次') for x in data['syntheses']]


# target = cv2.imread("item.png")
# template = cv2.imread("a.png")
# theight, twidth = template.shape[:2]
# result = cv2.matchTemplate(target,template,cv2.TM_SQDIFF_NORMED)
# cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
# min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
# #匹配值转换为字符串
# #对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
# #对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc

# strmin_val = str(min_val)
# #绘制矩形边框，将匹配区域标注出来
# #min_loc：矩形定点
# #(min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
# #(0,0,225)：矩形的边框颜色；2：矩形边框宽度
# print(min_loc)
# cv2.rectangle(target,min_loc,(min_loc[0]+twidth,min_loc[1]+theight),(0,0,225),2)

# cv2.imshow("MatchResult----MatchingValue="+strmin_val,target)
# cv2.waitKey()
# cv2.destroyAllWindows()
