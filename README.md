# lixianla
lixianla.com auto sign task


# 自动化任务

推荐部署在云函数。

# Github Action
请clone此项目，自行push到private项目，以免泄露数据，如果你头铁，自行fork并填入相应数据。


使用Github Action自动化任务也许存在[任务延迟](https://zhuanlan.zhihu.com/p/379365305)

根据测试，Github Acion任务将整个运行环境部署完成需要花费30s左右，如果有在0点准时打卡的需求，请优先考虑云函数、软路由部署。

在Acion中建议为main函数执行30s左右延迟，并将crontab提前为每天23:59运行（注意时区问题，北京时间比Github所使用时区快8个小时），理论上可以解决此问题，未经测试，请自行试验。

# workflows
```yaml
name: auto_task

on:
  schedule:
    - cron: "0 16 * * *"

  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.9
        uses: actions/setup-python@v2
        with:
                python-version: 3.9
                
                
      - name: Install dependencies
        run: |
              python -m pip install --upgrade pip
              pip install requests
              pip install ddddocr
              pip install bs4
      
      - name: Sign Task
        run: |
              python main.py
```

# 注意事项
由于[不可抗拒的力量](https://work.weixin.qq.com/nl/act/p/32d807ad4c554975)，企业微信推送方式弃用，切换为钉钉机器人。如有需要请自行查看commits

如果你的应用于2022年6月20日之前创建，或者拥有一个固定的公网非服务商IP，可以使用企业微信进行（更加美观的）图文推送。
