import sqlite3
import re
import requests

import json
from requests_html import HTMLSession


def getdata():
    session = HTMLSession()
    url = "https://cupfox.app/"
    h = session.get(url=url)
    pattern = r'tv_热门.*?tv_日本动画'
    data = re.search(pattern, h.html.html).group()
    datajson = json.loads(data[7:-9])
    id = 0
    cx = sqlite3.connect("test.db")
    cx.execute('''
    create table home(
    id int primary key not null,
    subjects TEXT);
    ''')
    # cu = cx.cursor()

    for line in datajson['subjects']:
        # print(line)
        # 插入数据
        # sql = 'insert into home(id,subjects) values("%s", "%s")' % (id, line)
        # 更新数据，有更新则替换，无则不需替换
        sql = 'replace into home(id, subjects) values("%s","%s")' % (id, line)
        cx.execute(sql)
        id += 1
        print(line)
        cx.commit()


def setdata():
    cx = sqlite3.connect("test.db")
    cursor = cx.execute("select * from home")
    # 查询数据
    list = []
    for row in cursor:
        list.append(row[1])
    return list


if __name__ == '__main__':
    getdata()
    setdata()



