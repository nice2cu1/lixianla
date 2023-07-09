import re
import hmac
import time
import json
import base64
import hashlib
import requests
import ddddocr
import urllib.parse
from bs4 import BeautifulSoup

DD_BOT_SECRET = ''  # 机器人创建时勾选 加签 获取SECRET
DD_BOT_TOKEN = ''  # 机器人Webhook中的access_token部分
PUSH_LOG = True  # 是否推送日志


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
    global push_msg
    login_attempts = 0
    print_log(f"################### {email} ###################")
    while login_attempts < 5:
        login_attempts += 1
        print_log(f"第{login_attempts}次尝试登录")
        login_session = requests.session()
        login_url = "https://lixianla.com/user-login.htm"
        login_response = login_session.get(login_url)
        login_bs = BeautifulSoup(login_response.text, 'html.parser')
        login_bs.prettify()
        # 登录验证码识别
        login_image_code = login_bs.select('.vcode')

        for image in login_image_code:
            img = image['src']
            img_code_url = f'https://lixianla.com/{img}'
            print_log("登录验证码地址：" + img_code_url)
            code_response = login_session.get(img_code_url)
            ocr = ddddocr.DdddOcr()
            login_code = ocr.classification(code_response.content)
            print_log("登录验证码：" + login_code)
        # 登录
        login_data = {
            'email': email,
            'password': password,
            'vcode': login_code,
        }
        login_response = login_session.post(login_url, data=login_data)
        login_response_bs = BeautifulSoup(login_response.content, 'html.parser')
        if login_response_bs.find(id='body').text.strip() == '密码错误':
            print_log("密码错误")
            push_msg += f"{email} 密码错误\n"
            break
        elif login_response_bs.find(id='body').text.strip() == '加密后长度有问题':
            print_log("加密后长度有问题")
            push_msg += f"{email} 加密后长度有问题\n"
            break
        elif login_response_bs.find(id='body').text.strip() == '邮箱不存在':
            print_log("邮箱不存在，请验证邮箱是否有误！")
            break
        elif login_response_bs.find(id='body').text.strip() == '验证码不正确':
            print_log("验证码不正确，将在3秒后重试")
            time.sleep(3)
        elif login_response_bs.find(id='body').text.strip() == '密码为空':
            print_log("密码为空")
            break
        elif login_response_bs.find(id='body').text.strip() == '登录成功':
            print_log("登录成功！\n开始执行签到")
            # 签到
            sign_attempts = 0
            while sign_attempts < 3:
                sign_attempts += 1
                sign_code_url = "https://lixianla.com/sg_sign.htm"
                sign_code_response = login_session.get(sign_code_url)
                sign_code_bs = BeautifulSoup(sign_code_response.content, 'html.parser')

                sign_code_script = sign_code_bs.findAll('script')  # 寻找所有script标签
                url_temp = "".join(re.findall("'s.*m'", str(sign_code_script))).replace("'", '')  # list转string、正则、去' 处理

                real_sign_url = f'https://lixianla.com/{url_temp}'
                sign_response = login_session.get(real_sign_url)
                sign_bs = BeautifulSoup(sign_response.content, 'html.parser')
                sign_bs.prettify()

                # 签到验证码识别
                sign_code = ''
                sign_img_code = sign_bs.select('.vcode')
                for image in sign_img_code:
                    img = image['src']
                    img_code_url = f'https://lixianla.com/{img}'
                    print_log("签到验证码地址：" + img_code_url)
                    code_response = login_session.get(img_code_url)
                    sign_code = ocr.classification(code_response.content)
                    print_log("签到验证码：" + sign_code)

                sign_data = {
                    'vcode': sign_code
                }
                time.sleep(1)
                sign_response = login_session.post(real_sign_url, data=sign_data)
                sign_response_bs = BeautifulSoup(sign_response.content, 'html.parser')
                print_log(
                    f"sign_response_bs.find(id='body').text.strip() ======== {sign_response_bs.find(id='body').text.strip()}")
                if sign_response_bs.find(id='body').text.strip() == '验证码错误!!!':
                    print_log("签到出错：" + sign_response_bs.find(id='body').text.strip() + ",将在1s后重试")
                    push_msg += f"{email}   签到出错：" + sign_response_bs.find(id='body').text.strip() + "\n"
                    time.sleep(1)
                elif sign_response_bs.find(id='body').text.strip() == "今天已经签过啦！":
                    print_log("今天已经签过啦！")
                    push_msg += f"{email} 今天已经签过啦！\n"
                    break
                elif '成功签到' in sign_response_bs.find(id='body').text.strip():
                    print_log(sign_response_bs.find(id='body').text.strip())
                    push_msg += f"{email}：{sign_response_bs.find(id='body').text.strip()}\n"
                    break
            break
        else:
            print_log("未知错误：" + login_response_bs.find(id='body').text.strip())
            push_msg += f"{email} 出现未被捕获的错误\n"
            time.sleep(1)
            break


def print_log(log: str):
    with open("log.txt", 'a', encoding="UTF-8") as file:
        file.write(log + "\n")
        print(log)


if __name__ == '__main__':
    push_msg = ""
    # 创建log文件
    with open("log.txt", 'w', encoding="UTF-8") as f:
        f.writelines("####日志文件####\n")

    # 读取配置文件
    try:
        with open("user.json", 'r') as f:
            user = json.load(f)
            for u in user:
                if u['email'] == "":
                    print_log("邮箱为空，跳过")
                    continue
                task(u['email'], u['password'])
            if PUSH_LOG:
                with open("log.txt", 'r', encoding="UTF-8") as f:
                    push_msg += f.read()
            dingding_bot(" LIXIANLA ", push_msg)
    except FileNotFoundError as e:
        print_log("配置文件不存在！！\n" + str(e))
    except json.decoder.JSONDecodeError as e:
        print_log("JSON格式错误！！\n" + str(e))
