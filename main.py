import configparser
import csv
import json
import socks
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import events
from telethon.errors import SessionPasswordNeededError
from telethon import utils
from telethon.tl.functions.channels import JoinChannelRequest


def get_bot_group(client):
    with client.conversation('@……bot') as conv:
        #向频道发送消息
        conv.send_message('balabala')
        message=conv.get_response()
        Group_url = []
        Group_name = []
        for i in message.entities:
            res = []
            if hasattr(i, 'url'):
                res.append(i.url)
                Group_url.append(res)
                message.click(i.url)
        mes=message.message.split('\n')
        for i in mes:
            name=[]
            name.append(i)
            Group_name.append(name)
        #点击下一页
        message.click(message.reply_markup.rows[0].buttons[1].text == '下一页 >>')

        while (1):
            messages = client.get_messages('@zh_groups_bot')
            #messages = client.get_messages('@hao1234bot')
            print(messages)
            #获取url
            for i in messages[0].entities:
                res = []
                if hasattr(i,'url'):
                    res.append(i.url)
                    Group_url.append(res)
            #分割出单独的群组名称
            mes = messages[0].message.split('\n')
            #获取群组名称
            for i in mes:
                name = []
                name.append(i)
                Group_name.append(name)
                #print(name)
            #根据页面按钮情况调整下一页点击位置
            if(len(messages[0].reply_markup.rows[0].buttons) == 3):
                messages[0].click(2)
            else:
                break

        #写入文件
        #dataframe = pd.DataFrame({'name':Group_name,'url':Group_url})
        #dataframe.to_csv(r"test.csv",sep=',',encoding='utf-8-sig')

def get_message(client):
    me = client.get_me()
    group_name_list=[]
    responses = client.iter_dialogs()
    if responses is not None:
        for response in responses:
            # if isinstance(response.entity, Channel):  # 过滤群组
            print(response)
            group_name_list.append(response.name)

    #循环爬取全部群组消息
    for name in group_name_list:
        id = name
        channel_item = client.get_entity(id)  # 获取channel这个entity的信息
        messages = client.iter_messages(id)

        #写入文件，或者数据库

        f = open(id + '.csv', 'w', encoding='utf-8-sig')
        csv_writer = csv.writer(f)
        csv_writer.writerow(["date", "sender", "message"])
        for message in messages:
            csv_writer.writerow([str(message.date), str(utils.get_display_name(message.sender)),
                                 str(message.message).replace('\r', '').replace('\n', '').replace('\t', '')])#过滤消息中的换行
        f.close()
        print(id, 'over')

def join_group(client,join_list):
    for id in join_list:
        channel = client.get_entity(id)
        client(JoinChannelRequest(channel))

'''
    主函数
    配置环境
    调用函数
'''
# 设置configuration值
api_id =
api_hash =
api_hash = str(api_hash)

phone =
username =
# 代理
host = '127.0.0.1'
port = 1080
proxy = (socks.SOCKS5, host, port)
# 创建连接
client = TelegramClient(username, api_id, api_hash, proxy=proxy)
client.start()
print("Client Created")
# 确认授权
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

client.get_dialogs()

get_bot_group(client)
get_message(client)
join_group(client,join_list)