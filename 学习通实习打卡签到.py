import re

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Zoom Edition Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36 (device:Redmi K30 Pro Zoom Edition) Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_6.2.8_android_phone_1050_234 (@Kalimdor)_8c0587fc07ee4c25bdbbb5d7a90d8152'
}
# 学习通用户名，手机号或者学号
username = ""
# 学习通密码
password = ""
# 学校ID，当用户名为学号时需要填写，为手机号时不需要填写
schoolid = ""
# 要打卡的地址名称、经度和纬度，可在http://api.map.baidu.com/lbsapi/getpoint/index.html中获取相应位置的坐标
address = "河南省郑州市金水区商务内环路15号绿地中心千玺广场"
# 打卡位置坐标，通过上面网址查询到的的坐标点可直接粘贴在这里
location = "113.733731,34.777027"
# 这个是学习通实习打卡中的“如果发生特殊情况未能正常打卡，可以在此填写理由”中的内容，可自行填写
remark = ""
session = requests.session()
res = session.post('https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(username, password, schoolid), headers=headers).json()
if res["result"]:
    res = session.get("http://cqcet.dgsx.chaoxing.com/form/mobile/signIndex", headers=headers)
    txt = res.text
    if txt != "您还没有被分配实习计划。":
        if "用户登录状态异常，请重新登录！" not in txt:
            planName = re.search(r"planName: '(.*)',", txt, re.I).groups()[0]
            _type = re.search(r"type: '(.*)',", txt, re.I).groups()[0]
            signType = re.search(r"signType: '(.*)',", txt, re.I).groups()[0]
            address = re.search(r'<input type="hidden" id="workAddress" value="(.*)"/>', txt, re.I).groups()[0]
            geolocation = re.search(r'<input type="hidden" id="workLocation" value="(.*)">', txt, re.I).groups()[0]
            remark = remark
            allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
            signSettingId = re.search(r'<input type="hidden" id="signSettingId" value="(.*)"/>', txt, re.I).groups()[0]
            data = {
                "planName": planName,
                "type": _type,
                "signType": signType,
                "address": address,
                "geolocation": geolocation,
                "remark": remark,
                "images": "",
                "offset": 0,
                "allowOffset": allowOffset,
                "signSettingId": signSettingId
            }
            res = session.post("http://cqcet.dgsx.chaoxing.com/form/mobile/saveSign", headers=headers, data=data)
            print(res.text)
        else:
            print("登录失败，请检查用户名密码后重试")
    else:
        res = session.get("https://www.dgsx.chaoxing.com/mobile/clockin/show", headers=headers)
        txt = res.text
        if res.status_code == 200:
            if "用户登录状态异常，请重新登录！" not in txt:
                clockinId = re.search(r'<input id="clockinId" type="hidden" value="(.*)">', txt, re.I).groups()[0]
                recruitId = re.search(r'<input type="hidden" id="recruitId" value="(.*)" />', txt, re.I).groups()[0]
                pcid = re.search(r'<input type="hidden" id="pcid" value="(.*)" />', txt, re.I).groups()[0]
                pcmajorid = re.search(r'<input type="hidden" id="pcmajorid" value="(.*)" />', txt, re.I).groups()[0]
                address = address
                geolocation = location
                remark = remark
                should_bntover = re.search(r'''<dd class="should_bntover" selid="(.*)" workStart='(.*)' workEnd='(.*)'>''', txt, re.I).groups()
                workStart = should_bntover[1]
                workEnd = should_bntover[2]
                allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
                offduty = 0
                changeLocation = re.search(r'<input type="text" name="location" id="location" value="(.*)" hidden/>', txt, re.I).groups()[0]
                if re.search(r'<input id="workLocation" type="hidden" >', txt, re.I) is None:
                    offset = re.search(r'<input id="workLocation" type="hidden" value="(.*)">', txt, re.I).groups()[0]
                else:
                    offset = "NaN"
                data = {
                    "id": clockinId,
                    "type": 0,
                    "recruitId": recruitId,
                    "pcid": pcid,
                    "pcmajorid": pcmajorid,
                    "address": address,
                    "geolocation": geolocation,
                    "remark": remark,
                    "workStart": workStart,
                    "workEnd": workEnd,
                    "images": "",
                    "allowOffset": allowOffset,
                    "offset": offset,
                    "offduty": offduty,
                    "changeLocation": changeLocation
                }
                res = session.post("https://www.dgsx.chaoxing.com/mobile/clockin/addclockin2", headers=headers, data=data)
                print(res.text)
            else:
                print("登录失败，请检查用户名密码后重试")
        else:
            print("您貌似并没有实习打卡任务")
else:
    print("登录失败，请检查您的用户名密码是否正确")
