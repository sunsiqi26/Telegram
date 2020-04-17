import json
import socks
import pymysql
#import cryptography
import csv
import pandas as pd

from datetime import date, datetime

from telethon import utils
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest, SendMessageRequest)
from telethon.tl.types import (
    PeerChannel,
    Channel, PeerUser)


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)



# Setting configuration values
api_id =
api_hash =

api_hash = str(api_hash).lower()

phone =
username =
host = '127.0.0.1'
port = 1080
proxy = (socks.SOCKS5, host, port)

db = pymysql.connect(host="127.0.0.1", user="root", port=3306, passwd="",
database="Telegram_db",use_unicode=True,charset="utf8mb4")
cursor = db.cursor()
sql="INSERT INTO rawData VALUES('id','groupName','memberName','date','speak');"

# Create the client and connect
client = TelegramClient(username, api_id, api_hash, proxy=proxy)
client.start()
print("Client Created")
# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

me = client.get_me()

'''

增量爬取
比对incremental文件中每个群组id对应的最后一个消息id的值
如果当前群组的最后一个消息id大于存储值则新增至数据库，同时更新incremental文件中对应的消息id

'''

df=pd.read_csv('incremental.csv',encoding='utf-8')
f1 = open('incremental.csv', 'a+', encoding='utf-8')
csv_writer = csv.writer(f1)

responses = client.iter_dialogs()
if responses is not None:
    for response in responses:
        #if isinstance(response.entity, Channel):  # 过滤群组
        if hasattr(response.message.to_id,'channel_id'):
            temp_id=response.message.to_id.channel_id
            if int(temp_id) not in list(df['group_id']):
                csv_writer.writerow([str(temp_id),-1])
f1.close()

idn=df['group_id']
last_message_id=df['last_message_id']

for name in idn:
    group_id=int(name)
    channel_item = client.get_entity(group_id)  #获取channel这个entity的信息
    messages = client.get_messages(group_id)
    mid=last_message_id[idn.index(group_id)]
    print('The last message id crawled last time: ',mid)

    for message in messages:
        if int(utils.get_message_id(message)) > mid:
            speak=str(message.message).replace('\r', '').replace('\n', '').replace('\t', '')
            sender=str(utils.get_display_name(message.sender))
            #对字段长度进行截断，防止数据库报错
            if len(speak)>500:
                speak=speak[:500]
            if len(sender)>80:
                sender=sender[:80]
            if len(speak)!=0 and speak!='None':
                cursor.execute("INSERT INTO rawData VALUES(null,%s,%s,%s,%s);",
                                (str(group_id), str(sender), str(str(message.date)[:19]),str(speak)))
        else:
            break
    df['last_message_id'][idn.index(group_id)] = utils.get_message_id(messages[0])
    df.to_csv('incremental.csv', index=False)
    db.commit()
    print(channel_item.title,'update commit success')
