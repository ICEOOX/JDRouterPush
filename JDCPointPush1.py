# 京东云无线路由宝推送
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
# 发送钉钉消息
def sendinfo_ding(token,secret,data):
    dic=get_timestamp_and_sign_by_secret(secret)
    timestamp=dic['timestamp']
    sign=dic['sign']
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s' %(token,timestamp,sign)  #你的机器人webhook地址
    headers = {'Content-Type': 'application/json'}
    f = requests.post(url, data=json.dumps(data), headers=headers)
# 获取密签
def get_timestamp_and_sign_by_secret(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return {"timestamp":timestamp,"sign":sign}
# 获取可用积分
def get_jd_total_avail_point(wskey):
    url='https://router-app-api.jdcloud.com/v1/regions/cn-north-1/pinTotalAvailPoint'
    headers = {'Content-Type': 'application/json','wskey':wskey}
    rsp=requests.get(url,headers=headers)
    data=(json.loads(rsp.text)['result']['totalAvailPoint'])
    return {'totalAvailPoint':data}
# 获取积分详情
def get_jd_detail(wskey):
    url='https://router-app-api.jdcloud.com/v1/regions/cn-north-1/todayPointDetail?sortField=today_point&sortDirection=DESC&pageSize=15&currentPage=1'
    headers = {'Content-Type': 'application/json','wskey':wskey}
    rsp=requests.get(url,headers=headers)
    data=(json.loads(rsp.text)['result'])
    items=data['pointInfos']
    total_today_point=0
    total_all_point=0
    dic={}
    dic['todayDate']=data['todayDate']
    dic['items']=[]
    for item in items:
        mac=item['mac']
        today_point=item['todayPointIncome']
        all_point=item['allPointIncome']
        total_today_point+=int(today_point)
        total_all_point+=int(all_point)
        dic['items'].append(item)
    dic['total_today_point']=total_today_point
    dic['total_all_point']=total_all_point
    return dic
# 发送京东路由宝日报
def send_jd_router(wskey):
    dic=get_jd_detail(wskey)
    msg='# 京东路由宝日报\n'
    msg+='## %s \n' %(dic['todayDate'])
    msg+=('> 今日获取总积分为**%d**分，对应金钱为 **%.2f**元\n' %(dic['total_today_point'],float(dic['total_today_point'])/100))
    for item in dic['items']:
        msg+=('>> 设备**%s** \n' %(item['mac']))
        msg+=('>>> 今日获取积分为**%s**分，对应金钱为 **%.2f**元 \n\n' %(item['todayPointIncome'],float(item['todayPointIncome'])/100))
    msg+=('> 累计总积分为 **%s** 分,对应金钱 **%.2f** 元 \n\n' %(dic['total_all_point'],float(dic['total_all_point'])/100))
    dic=get_jd_total_avail_point(wskey)
    msg+=('> 目前可用积分为 **%s** 分,对应金钱 **%.2f** 元' %(dic['totalAvailPoint'],float(dic['totalAvailPoint'])/100))

# 钉钉机器人token和sercret
    token=""
    secret=""
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title":"京东云路由宝日报",
            "text": msg
            },
    }
    sendinfo_ding(token,secret,data)
    

# 配置文件
wskey=''
send_jd_router(wskey)