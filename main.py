import code
import random
import time
import requests
from bs4 import BeautifulSoup
import json
import ddddocr
import re

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

def wecom_app(title: str, content: str):
    """
    通过 企业微信 APP 推送消息。
    """

    corpid = '' # 企业id
    corpsecret = '' # 应用凭证密钥
    touser = '@all' # 消息推送范围，@all代表整个部门
    agentid = '' # 应用id
    try:
        media_id = '-6OHBy9UbMgQVDd4F1tbSWKjDhCf5o4ay' # 素材库图片media_id
    except IndexError:
        media_id = ""
    wx = WeCom(corpid, corpsecret, agentid)
    if not media_id:
        message = title + "\n\n" + content
        response = wx.send_text(message, touser)
    else:
        response = wx.send_mpnews(title, content, media_id, touser)

    if response == "ok":
        print("企业微信推送成功！")
    else:
        print("企业微信推送失败！错误信息如下：\n", response)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "nice2cu1",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]




if __name__=="__main__":
    # time.sleep(random.randint(0,5)) #随机延迟
    # sign()

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
            'email': "", #邮箱
            'password': "", #密码 md5 32位小写
            "vcode": code #验证码
        }
        login_response = login_session.post(login_url, data= login_data)
        login_response_bs = BeautifulSoup(login_response.content, 'html.parser')
        if login_response_bs.find(id='body').text.strip() == '密码错误':
            print("登录出错："+login_response_bs.find(id='body').text.strip())
        elif login_response_bs.find(id='body').text.strip() == '验证码不正确' :
            print("登录出错："+login_response_bs.find(id='body').text.strip()+",将在1s后重试")
            time.sleep(1)
        elif login_response_bs.find(id='body').text.strip() == '登录成功':
            print(login_response_bs.find(id='body').text.strip())
        else :
            print('else :'+login_response_bs.find(id='body').text.strip())

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
                wecom_app(sign_response_bs.find(id='body').text.strip(),sign_response_bs.find(id='body').text.strip())
            elif sign_response_bs.find(id='body').text.strip() in '成功签到！' :
                sign_msg = 1               
                print(sign_response_bs.find(id='body').text.strip())  
                wecom_app('签到成功',sign_response_bs.find(id='body').text.strip())   
            print (f"count = {sign_response_bs.find(id='body').text.strip()}")
            print(f"msg = {sign_msg}")
            print("-----------------------------------")                               
