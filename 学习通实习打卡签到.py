import json
import re
import time
from tkinter import filedialog

import filetype
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
# 新版实习打卡中要提交的图片列表，填写时请使用引号包裹后写在中括号内，如下面注释所示
# pictureAry = ["3acf16259def65456fc2a68ab5e10d96"]
# 要设置多个图片请用英文逗号隔开，如下面注释所示
# pictureAry = ["3acf16259def65456fc2a68ab5e10d96","3acf16259def65456fc2a68ab5e10d95","3acf16259def65456fc2a68ab5e10d94"]
pictureAry = []


def new_clockin(session):
    url = "https://sx.chaoxing.com/internship/planUser/myPlanList"
    res = session.get(url, headers=headers)
    if res.url == url:
        res = res.json()
    else:
        return [0, "登录失败，请检查用户名密码后重试"]
    if res["result"] == 0 and len(res["data"]) > 0:
        planlist = []
        for d in res["data"]:
            tempdict = {"planName": d["planName"], "planId": d["planId"], "fid": d["fid"], "planUserId": d["id"]}
            if d["planStatus"] == 1:
                tempdict["planStatus"] = "进行中"
            elif d["planStatus"] == 2:
                tempdict["planStatus"] = "已结束"
            elif d["planStatus"] == 3:
                tempdict["planStatus"] = "未开始"
            if d["sxStatus"] == 0:
                tempdict["sxStatus"] = "未实习"
            elif d["sxStatus"] == 1:
                tempdict["sxStatus"] = "实习中"
            elif d["sxStatus"] == 2:
                tempdict["sxStatus"] = "免实习"
            elif d["sxStatus"] == 3:
                tempdict["sxStatus"] = "终止实习"
            tempdict["planStartTime"] = d["planStartTime"]
            tempdict["planEndTime"] = d["planEndTime"]
            tempdict["recruitNames"] = d["recruitNames"]
            planlist.append(tempdict)
        print("{} {:<50} {:<10} {:<6} {:<23} {}".format("ID", "实习计划名称", "实习计划状态", "实习状态", "实习时间", "实习岗位"))
        print("-" * 120)
        inputid = 0
        for d in planlist:
            inputid += 1
            print("{:<2} {:<40} {:<12} {:<7} {:<25} {}".format(inputid, d["planName"], d["planStatus"], d["sxStatus"], d["planStartTime"] + "-" + d["planEndTime"], d["recruitNames"]))
        while True:
            inputid = input("输入要进行实习打卡的ID：")
            try:
                inputid = int(inputid)
                if 0 < inputid <= len(planlist):
                    break
                else:
                    print("ID输入错误，请重新输入")
            except ValueError:
                print("ID输入错误，请重新输入")
        select_plan = planlist[inputid-1]
        getDataByIdurl = "https://sx.chaoxing.com/internship/planUser/getDataById?planId={}&planUserId={}".format(select_plan["planId"], select_plan["planUserId"])
        res = session.get(getDataByIdurl, headers=headers)
        if res.url == getDataByIdurl:
            res = res.json()
            if res["result"] == 0 and res["data"] is not None:
                if len(res["data"]["userPeriods"]) > 0:
                    workStart = res["data"]["userPeriods"][0]["planUserRecruit"]["recruitVo"]["workStart"]
                    workEnd = res["data"]["userPeriods"][0]["planUserRecruit"]["recruitVo"]["workEnd"]
                else:
                    workStart = ""
                    workEnd = ""
                dgsxpcurl = "https://sx.chaoxing.com/internship/dgsxpc/{}".format(select_plan["planId"])
                res = session.get(dgsxpcurl, headers=headers)
                if res.url == dgsxpcurl:
                    res = res.json()
                    if res["result"] == 0 and res["data"] is not None:
                        isontimesign = res["data"]["isontimesign"]
                        allowOffset = res["data"]["offset"] or 2000
                        dateurl = "https://sx.chaoxing.com/internship/clockin-user/get/stu/{}/date?date={}".format(select_plan["planId"], time.strftime("%Y-%m-%d"))
                        res = session.get(dateurl, headers=headers)
                        if res.url == dateurl:
                            res = res.json()
                            if res["result"] == 0 and res["data"] is not None:
                                cxid = res["data"]["cxid"]
                                clockinId = res["data"]["id"]
                                while True:
                                    clockintype = input("请输入上下班打卡状态，输入0为上班打卡，输入1为下班打卡：")
                                    if clockintype != "0" and clockintype != "1":
                                        print("输入错误，请重新输入")
                                    elif clockintype == "0":
                                        statusName = "上班"
                                        break
                                    else:
                                        statusName = "下班"
                                        break
                                recruitId = res["data"]["recruitId"]
                                pcid = res["data"]["pcid"]
                                pcmajorid = res["data"]["pcmajorid"]
                                offduty = 0
                                if isontimesign:
                                    addclockinurl = "https://sx.chaoxing.com/internship/clockin-user/stu/addclockin/{}".format(cxid)
                                else:
                                    addclockinurl = "https://sx.chaoxing.com/internship/clockin-user/stu/addclockinOnceInDay/{}".format(cxid)
                                data = {
                                    "id": clockinId,
                                    "type": clockintype,
                                    "recruitId": recruitId,
                                    "pcid": pcid,
                                    "pcmajorid": pcmajorid,
                                    "address": address,
                                    "geolocation": location,
                                    "remark": remark,
                                    "workStart": workStart,
                                    "workEnd": workEnd,
                                    "images": json.dumps(pictureAry) if len(pictureAry) > 0 else "",
                                    "allowOffset": allowOffset,
                                    "offset": "NaN",
                                    "offduty": offduty,
                                    "codecolor": "",
                                    "havestar": "",
                                    "worktype": "",
                                    "changeLocation": "",
                                    "statusName": statusName,
                                    "shouldSignAddress": ""
                                }
                                res = session.post(addclockinurl, headers=headers, data=data)
                                if res.url == addclockinurl:
                                    return [1, res.text]
                                else:
                                    return [0, "登录失败，请检查用户名密码后重试"]
                            else:
                                return [2, res["errorMsg"]]
                        else:
                            return [0, "登录失败，请检查用户名密码后重试"]
                    else:
                        return [2, res["errorMsg"]]
                else:
                    return [0, "登录失败，请检查用户名密码后重试"]
            else:
                return [2, res["errorMsg"]]
        else:
            return [0, "登录失败，请检查用户名密码后重试"]
    else:
        return [2, "未找到新版实习打卡任务"]


def old_clockin1(session):
    res = session.get("https://www.dgsx.chaoxing.com/form/mobile/signIndex", headers=headers)
    txt = res.text
    if txt != "您还没有被分配实习计划。":
        if "用户登录状态异常，请重新登录！" not in txt:
            planName = re.search(r"planName: '(.*)',", txt, re.I).groups()[0]
            clockin_type = re.search(r"type: '(.*)',", txt, re.I).groups()[0]
            signType = re.search(r"signType: '(.*)',", txt, re.I).groups()[0]
            workAddress = re.search(r'<input type="hidden" id="workAddress" value="(.*)"/>', txt, re.I).groups()[0]
            geolocation = re.search(r'<input type="hidden" id="workLocation" value="(.*)">', txt, re.I).groups()[0]
            allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
            signSettingId = re.search(r'<input type="hidden" id="signSettingId" value="(.*)"/>', txt, re.I).groups()[0]
            data = {
                "planName": planName,
                "type": clockin_type,
                "signType": signType,
                "address": workAddress,
                "geolocation": geolocation,
                "remark": remark,
                "images": "",
                "offset": 0,
                "allowOffset": allowOffset,
                "signSettingId": signSettingId
            }
            res = session.post("https://www.dgsx.chaoxing.com/form/mobile/saveSign", headers=headers, data=data)
            return [1, res.text]
        else:
            return [0, "登录失败，请检查用户名密码后重试"]
    else:
        return [2, "未找到旧版页面1实习打卡任务"]


def old_clockin2(session):
    res = session.get("https://i.chaoxing.com/base/cacheUserOrg", headers=headers).json()
    site = res["site"]
    is_find = False
    for d in site:
        fid = str(d["fid"])
        session.cookies.set("wfwfid", fid)
        res = session.get("https://www.dgsx.chaoxing.com/mobile/clockin/show", headers=headers)
        txt = res.text
        if res.status_code == 200:
            if "alert('请先登录');" in txt or 'alert("实习计划已进入总结期或实习已终止，无法签到");' in txt:
                continue
            elif "用户登录状态异常，请重新登录！" not in txt:
                clockinId = re.search(r'<input id="clockinId" type="hidden" value="(.*)">', txt, re.I).groups()[0]
                recruitId = re.search(r'<input type="hidden" id="recruitId" value="(.*)" />', txt, re.I).groups()[0]
                pcid = re.search(r'<input type="hidden" id="pcid" value="(.*)" />', txt, re.I).groups()[0]
                pcmajorid = re.search(r'<input type="hidden" id="pcmajorid" value="(.*)" />', txt, re.I).groups()[0]
                geolocation = location
                should_bntover = re.search(r'''<dd class="should_bntover" selid="(.*)" workStart='(.*)' workEnd='(.*)'>''', txt, re.I).groups()
                workStart = should_bntover[1]
                workEnd = should_bntover[2]
                allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
                offduty = 0
                changeLocation = re.search(r'<input type="text" name="location" id="location" value="(.*)" hidden/>', txt, re.I).groups()[0]
                if re.search(r'<input id="workLocation" type="hidden" >', txt, re.I) is None:
                    if re.search(r'<input id="workLocation" type="hidden" value="(.*)">', txt, re.I) is None:
                        offset = "NaN"
                    else:
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
                print("旧版页面2打卡结果", res.text)
                is_find = True
                break
            else:
                print("登录失败，请检查用户名密码后重试")
    if is_find is False:
        print("您貌似并没有实习打卡任务")


def clockin_main():
    session = requests.session()
    resp = session.post('https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(username, password, schoolid), headers=headers).json()
    if resp["result"]:
        print("登录成功，正在搜索新版实习打卡任务")
        result = new_clockin(session)
        if result[0] == 1:
            print("新版打卡结果", result[1])
        elif result[0] == 2:
            print(result[1])
            print("将继续查询旧版页面1实习打卡任务")
            result = old_clockin1(session)
            if result[0] == 1:
                print("旧版页面1打卡结果", result[1])
            elif result[0] == 2:
                print(result[1])
                print("将继续查询旧版页面2实习打卡任务")
                old_clockin2(session)
            else:
                print(result[1])
        else:
            print(result[1])
    else:
        print("登录失败，请检查您的用户名密码是否正确")
    print("打卡执行结束")
    time.sleep(3)


def upload_img():
    session = requests.session()
    resp = session.post('https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(username, password, schoolid), headers=headers).json()
    if resp["result"]:
        while True:
            filepath = filedialog.askopenfilename(title="选择拍照图片", filetypes=(("图片文件", "*.jpg;*.png;*.gif;*.webp;*.bmp"),))
            file_type = filetype.guess(filepath)
            if file_type is None:
                print("您选择的文件不是图片文件，请重新选择")
                time.sleep(3)
            elif file_type.extension != "jpg" and file_type.extension != "png" and file_type.extension != "gif" and file_type.extension != "webp" and file_type.extension != "bmp":
                print("您选择的文件不是图片文件，请重新选择")
                time.sleep(3)
            else:
                break
        uploadurl = "https://sx.chaoxing.com/internship/usts/file"
        with open(filepath, 'rb') as file:
            files = {'file': file}
            res = session.post(uploadurl, headers=headers, files=files)
        if res.url == uploadurl:
            res = res.json()
            if res["result"] == 0:
                print("上传成功，文件ID为", res["data"]["objectid"], "可将其粘贴至pictureAry列表中，粘贴后请重新运行脚本使其生效")
            else:
                print("上传失败", res["errorMsg"])
        else:
            print("登录失败，请检查您的用户名密码是否正确")
    else:
        print("登录失败，请检查您的用户名密码是否正确")
    time.sleep(3)


if __name__ == '__main__':
    while True:
        print("欢迎使用学习通实习打卡签到脚本")
        print("0.开始打卡")
        print("1.上传打卡图片")
        print("2.退出")
        useid = input("请输入功能序号：")
        if useid == "0":
            clockin_main()
        elif useid == "1":
            upload_img()
        else:
            break
