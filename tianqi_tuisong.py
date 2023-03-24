# weather.py
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import json


class SendMessage():  # 定义发送消息的类
    def __init__(self):
        date = self.get_date()  # 获取当前日期
        weather = self.get_weather()
        self.dataJson = {
            "city":'坪山' +'\n',
            "date": date + '\n',
            "weather": weather + '\n',

        }
        self.appID = 'wxe3d84ed13378589a'  # appid 注册时有
        self.appsecret = '70d3881a777d88d40e69b81e85b2e7b5'  # appsecret 同上
        self.template_id = 'ky9nrTxeH2vakKmWkHaUtuVcpYEYtzRUBvR88sC8e9I'  # 模板id
        self.access_token = self.get_access_token()  # 获取 access token
        self.opend_ids = self.get_openid()  # 获取关注用户的openid

    def get_weather(self):
        """请求获得网页内容"""
        url = "http://www.weather.com.cn/weather/101280609.shtml"
        sysdate = datetime.date.today()
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print("成功访问")
        html = r.text
        bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
        body = bs.body
        # 下面爬取当天的数据
        data = body.find('div', {'id': '7d'})
        ul = data.find('ul')
        lis = ul.find_all('li')
        final_list = []

        for day in lis:
            date = day.find('h1').string  # 找到日期

            if date.string.split('日')[0] == str(sysdate.day):
                temp_list = []

                date = day.find('h1').string  # 找日期
                temp_list.append(date)

                info = day.find_all('p')  # 找p标签
                temp_list.append(info[0].string)  # 天气

                if info[1].find('span') is None:
                    temperature_highest = ' '  # 判断是否有最高温
                else:
                    temperature_highest = info[1].find('span').string
                    temperature_highest = temperature_highest.replace('℃', ' ')

                if info[1].find('i') is None:  # 判断是否有最低温
                    temperature_lowest = ' '
                else:
                    temperature_lowest = info[1].find('i').string
                    temperature_lowest = temperature_lowest.replace('℃', ' ')

                temp_list.append(temperature_highest)  # 添加最高温
                temp_list.append(temperature_lowest)  # 添加最低温

                final_list.append(temp_list)
                return final_list[0][1] + '\n温度：' + final_list[0][3].strip() + '~' + \
                       final_list[0][2].strip() + '℃'

    def get_date(self):
        sysdate = datetime.date.today()  # 只获取日期
        now_time = datetime.datetime.now()  # 获取日期和当前时间
        week_day = sysdate.isoweekday()  # 获取周几

        week = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期天']
        return '现在是' + str(now_time)[0:16] + ' ' + week[week_day - 1]  # 2023-03-23 19:27  4

    def get_access_token(self):
        """
        获取access_token
        """
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'. \
            format(self.appID, self.appsecret)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
        }
        response = requests.get(url, headers=headers).json()
        access_token = response.get('access_token')
        return access_token

    def get_openid(self):
        """
        获取所有用户id
        :return:
        """
        next_openid = ''
        url_openid = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s' % (
            self.access_token, next_openid)
        ans = requests.get(url_openid)
        open_ids = json.loads(ans.content)['data']['openid']
        return open_ids

    def sendmsg(self):
        """
        给所有用户发送消息
        """
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(self.access_token)

        if self.opend_ids != '':
            for open_id in self.opend_ids:
                body = {
                    "touser": open_id,
                    "template_id": self.template_id,
                    "url": "https://www.baidu.com/",
                    "topcolor": "#FF0000",
                    # 对应模板中的数据模板
                    "data": {
                        "body": {
                            "value": self.dataJson.get("body"),
                            "color": "#EA0000"
                        },
                        "weather": {
                            "value": self.dataJson.get("weather"),
                            "color": "#00EC00"
                        },
                        "date": {
                            "value": self.dataJson.get("date"),
                            "color": "#6F00D2"
                        },
                        "city":{
                            "value":self.dataJson.get("city"),
                            "color":"#0000FF"
                        }

                    }
                }
                data = bytes(json.dumps(body, ensure_ascii=False).encode('utf-8'))  # 将数据编码json并转换为bytes型
                response = requests.post(url, data=data)
                result = response.json()  # 将返回信息json解码
                print(result)  # 根据response查看是否广播成功
        else:
            print("当前没有用户关注该公众号！")


if __name__ == '__main__':
    sends = SendMessage()
    sends.sendmsg()
