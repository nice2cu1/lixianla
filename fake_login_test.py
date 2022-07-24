import random
import time


msg = 0

while msg != 1:
    print("login....")
    time.sleep(1)
    count = random.randint(0,2)
    if count == 0:
        msg = 1
        print ('签到成功')
    elif count == 1:
        msg = 0
        print ('验证码出错')
    elif count == 2:
        msg = 1
        print ('已经签到过了')
    print (f"count = {count}")
    print(f"msg = {msg}")
    print("-----------------------------------")
else :
    print('login success')