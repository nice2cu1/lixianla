import re
import hmac
import time
import json
import random
import base64
import hashlib
import requests
import ddddocr
import urllib.parse
from bs4 import BeautifulSoup

## Contab 
# 
# 0 0 * * *
#
# 每天0点执行
#
#  The script encoding is UTF-8, if you cannot see Chinese comments, please modify the file encoding
#  The script encoding is UTF-8, if you cannot see Chinese comments, please modify the file encoding

#没有详细分析时编写的代码，无用，仅作记录。
# def sign():
#         url = "https://lixianla.com/sg_sign-lx-1059945667.htm"
#         headers = {
#         'cookie': '' #cookie
#         } 
#         response = requests.request("GET", url, headers=headers)
#         soup = BeautifulSoup(response.text,'html.parser')
#         wecom_app(soup.h4.text.strip(),soup.h4.text.strip())

DD_BOT_SECRET = '' #机器人创建时勾选 加签 获取SECRET
DD_BOT_TOKEN =  '' #机器人Webhook中的access_token部分

def dingding_bot(title: str, content: str) -> None:
    """
    使用 钉钉机器人 推送消息。
    """
    if not DD_BOT_SECRET or not DD_BOT_TOKEN:
        print("钉钉机器人 服务的 DD_BOT_SECRET 或者 DD_BOT_TOKEN 未设置!!\n取消推送")
        return
    print("钉钉机器人 服务启动")

    timestamp = str(round(time.time() * 1000))
    secret_enc = DD_BOT_SECRET.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, DD_BOT_SECRET)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n{content}"}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if not response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print("钉钉机器人 推送失败！")

def task(email: str, password: str):
    login_msg = ''
    while login_msg != '登录成功':
        login_session = requests.session()
        login_url = "https://lixianla.com/user-login.htm"
        login_response = login_session.get(login_url)
        login_bs = BeautifulSoup(login_response.text,'html.parser')
        login_bs.prettify()
        #登录验证码识别
        login_image_code = login_bs.select('.vcode')
        for image in login_image_code:
            img = image['src']
            img_code_url=f'https://lixianla.com/{img}'
            code_response = login_session.get(img_code_url)
            ocr = ddddocr.DdddOcr(show_ad=False)
            code = ocr.classification(code_response.content)
            print("登录验证码："+code)
        #登录数据
        login_data = {
            'email': email, #邮箱
            'password': password, #密码  32位小写md5
            "vcode": code #验证码
        }
        login_response = login_session.post(login_url, data= login_data)
        login_response_bs = BeautifulSoup(login_response.content, 'html.parser')
        if login_response_bs.find(id='body').text.strip() == '密码错误':
            print("登录出错："+login_response_bs.find(id='body').text.strip())
            dingding_bot('密码错误','请检查密码是否为32位小写md5加密！')   
            break
        elif login_response_bs.find(id='body').text.strip() == '邮箱不存在':
            print("登录出错："+login_response_bs.find(id='body').text.strip())
            dingding_bot('邮箱不存在，请验证邮箱是否有误！')
            break
        elif login_response_bs.find(id='body').text.strip() == '验证码不正确' :
            print("登录出错："+login_response_bs.find(id='body').text.strip()+",将在1s后重试")
            time.sleep(1)
        elif login_response_bs.find(id='body').text.strip() == '登录成功':
            print(login_response_bs.find(id='body').text.strip())
        else :
            print('登录出错：'+login_response_bs.find(id='body').text.strip())
            dingding_bot('登录出错',login_response_bs.find(id='body').text.strip())
            break

        login_msg = login_response_bs.find(id='body').text.strip()
    else:    
        #签到
        print('开始执行签到....')
        sign_msg = 0
        while sign_msg != 1:     
            sign_code_url = 'https://lixianla.com/sg_sign.htm'
            sign_code_response = login_session.get(sign_code_url)
            sign_code_bs = BeautifulSoup(sign_code_response.content,'html.parser')

            sign_code_script = sign_code_bs.findAll('script') #寻找所有script标签
            url_temp = "".join(re.findall("'s.*m'", str(sign_code_script))).replace("'",'') #list转string、正则、去' 处理

            real_sign_url = f'https://lixianla.com/{url_temp}'
            cookie = login_response.cookies
            sign_response = login_session.get(real_sign_url)
            sign_bs = BeautifulSoup(sign_response.content,'html.parser')
            sign_bs.prettify()

            sign_code = ''
            #签到验证码识别
            sign_img_code = sign_bs.select('.vcode')
            for image in sign_img_code:
                img_code_url=f'https://lixianla.com/{img}'
                code_response = login_session.get(img_code_url)
                sign_code = ocr.classification(code_response.content)
                print("签到验证码："+sign_code)

            sign_data = {
                'vcode' : sign_code
            }
                
            sign_response = login_session.post(real_sign_url,data=sign_data)
            sign_response_bs = BeautifulSoup(sign_response.content, 'html.parser')
            print(f"sign_response_bs.find(id='body').text.strip() ======== {sign_response_bs.find(id='body').text.strip()}")
            if sign_response_bs.find(id='body').text.strip() == '验证码错误!!!':
                sign_msg = 0               
                print("签到出错："+sign_response_bs.find(id='body').text.strip()+",将在1s后重试")
                time.sleep(1)
            elif sign_response_bs.find(id='body').text.strip() == '今天已经签过啦！':
                sign_msg = 1
                dingding_bot(sign_response_bs.find(id='body').text.strip(),sign_response_bs.find(id='body').text.strip())
                break
            elif '成功签到' in sign_response_bs.find(id='body').text.strip() :
                sign_msg = 1               
                print(sign_response_bs.find(id='body').text.strip())  
                dingding_bot('签到成功',sign_response_bs.find(id='body').text.strip())
                break
            print (f"count = {sign_response_bs.find(id='body').text.strip()}")
            print(f"msg = {sign_msg}")
            print("-----------------------------------")

if __name__=="__main__":
    # time.sleep(random.randint(0,5)) #随机延迟
    # sign()                         
    with open('user.json', 'r', encoding='utf-8') as f:
        user = json.load(f)
    for i in user:
        task(i['email'],i['password'])
        time.sleep(random.randint(0,5))