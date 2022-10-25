import sqlite3
import re
import requests

import json
from requests_html import HTMLSession


def getvip(id=1, address= '',arrange='',plot='',language='',year=''):
    session = HTMLSession()
    url = "https://www.freeok.vip/vodshow/{0}-{1}-{2}-{3}-{4}-------{5}.html".format(id, address, plot, arrange, language, year)
    h = requests.get(url=url)
    pattern = 'original.*?referrerpolicy'
    data = re.findall(pattern, h.text)
    id = 0
    cx = sqlite3.connect("test.db")
    # 删除表
    # cx.execute('''
    # DROP TABLE class;
    # ''')
    # 创建表
    # cx.execute('''
    # create table class(
    # original char(100),
    # alt char(50));
    # ''')
    for item in data:
        datatext = item[0:-16].replace("=", ":")
        datatext = datatext.replace("original", '"original"')
        datatext = datatext.replace("alt", '"alt"')
        datatext = datatext.replace(" ", ',')
        datatext = "{" + datatext + "}"
        datajson = json.loads(datatext)
        # 插入数据
        # sql = 'insert into class(original,alt) values("%s", "%s")' % (datajson["original"], datajson["alt"])
        # 更新数据，有更新则替换，无则不需替换
        sql = 'replace into class(original, alt) values("%s","%s")' % (datajson["original"], datajson["alt"])
        cx.execute(sql)
        id += 1
        cx.commit()


def setvip():
    cx = sqlite3.connect("test.db")
    cursor = cx.execute("select * from class")
    # 查询数据
    list = []
    for row in cursor:
        datatext = dict(zip(["original", "alt"], [row[0], row[1]]))
        if datatext not in list:
            list.append(datatext)
    return json.dumps(list, ensure_ascii=False)


def getdata(id=1, address= '',arrange='',plot='',language='',year='',limit=''):
    session = HTMLSession()
    url = "https://www.freeok.vip/vodshow/{0}-{1}-{2}-{3}-{4}----{6}---{5}.html".format(id, address, plot, arrange, language, year,limit)
    h = session.get(url=url)
    pattern = 'original.*?referrerpolicy'
    patternone = 'note.*?div'
    patterntwo = '"/voddetail.*?title'
    data = re.findall(pattern, h.html.html)
    dataone = re.findall(patternone, h.html.html)
    datatwo = re.findall(patterntwo, h.html.html)
    list = []
    l = []
    t = []
    # 处理数据，通过正则找出三个数据，然后添加到字典里面
    for item in data:
        datatext = item[0:-16].replace("=", ":")
        datatext = datatext.replace("original", '"original"')
        datatext = datatext.replace("alt", '"alt"')
        datatext = datatext.replace(" ", ',')
        datatext = "{" + datatext + "}"
        datajson = json.loads(datatext)
        for itemone in dataone:
            name = itemone[6:-5]
            l.append(name)
            # name = dict(zip(["name"], [itemone[6:-5]]))
        for itemtwo in datatwo:
            idname = itemtwo[1:-7]
            t.append(idname)
        dataname = dict(zip(["name"], l))
        idname = dict(zip(["icon"], t))
        sum = dict(dataname,**datajson)
        list.append(dict(idname, **sum))
    list = dict(zip(["data"], [list]))
    return json.dumps(list, ensure_ascii=False)


if __name__ == '__main__':
    # print(getdata())
    getdata()
    # getvip()
    # setvip()



