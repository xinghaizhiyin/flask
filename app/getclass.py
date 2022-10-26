import sqlite3
import re
import time

import requests,time
from flask import request
import json
from requests_html import HTMLSession


def getvip(id=1):
    cx = sqlite3.connect("test.db")
    # 删除表 animation movie tv
    # cx.execute('''
    # DROP TABLE animation;
    # ''')
    # 创建表
    # cx.execute('''
    # create table animation(
    # img char(200),
    # name char(100),
    # icon char(100)
    # );''')
    session = HTMLSession()
    url = "https://www.freeok.vip/vodshow/{}-----------.html".format(id)
    h = session.get(url=url)
    print(url)
    pattern = 'original.*?referrerpolicy'
    data = re.findall(pattern, h.html.html)
    patternone = 'note.*?div'
    dataone = re.findall(patternone, h.html.html)
    list = []
    listone = []
    listtwo = []

    # 获取图片和名称，并写入数据库
    for item in data:
        datatext = item[0:-16].replace("=", ":")
        datatext = datatext.replace("original", '"original"')
        datatext = datatext.replace("alt", '"alt"')
        datatext = datatext.replace(" ", ',')
        datatext = "{" + datatext + "}"
        datajson = json.loads(datatext)
        list.append(datajson['original'])
        listone.append(datajson['alt'])
    # 获取影片记录，1080p，hd
    for itemone in dataone:
        listtwo.append(itemone[6:-5])
    listsum = zip(list, listone, listtwo)
    if id == 1:
        cx.execute('Delete From movie')
        for item, item1, item2 in listsum:
            sql = 'insert into movie(img,name,icon) values("%s","%s","%s")' % (item, item1, item2)
            cx.execute(sql)
    elif id == 2:
        cx.execute('Delete From tv')
        for item, item1, item2 in listsum:
            sql = 'insert into tv(img,name,icon) values("%s","%s","%s")' % (item, item1, item2)
            cx.execute(sql)
    elif id == 3:
        cx.execute('Delete From animation')
        for item, item1, item2 in listsum:
            sql = 'insert into animation(img,name,icon) values("%s","%s","%s")' % (item, item1, item2)
            cx.execute(sql)
        # 插入数据
        # sql = 'insert into class(id,img,name, icon) values("%s","%s","%s")' % (item, item1, item2)
        # 更新数据，有更新则替换，无则不需替换
        # sql = 'replace into class(img,name, icon) values("%s","%s","%s")' % (item, item1, item2)
        # 删除数据
        # sql = 'Delete From class'
        # cx.execute(sql)
    cx.commit()


def getsum():
    getvip()
    time.sleep(10)
    getvip(2)
    time.sleep(10)
    getvip(3)


def setvip(id=1):
    cx = sqlite3.connect("test.db")
    if id == 1:
        cursor = cx.execute("select * from movie")
    elif id == 2:
        cursor = cx.execute("select * from tv")
    elif id == 3:
        cursor = cx.execute("select * from animation")
    # 查询数据
    list = []
    for row in cursor:
        img = dict(zip(["img"], [row[0]]))
        icon = dict(zip(["icon"], [row[2]]), **img)
        name = dict(zip(["name"], [row[1]]), **icon)
        list.append(name)
    # list = dict(zip(["data"], [list]))
    return json.dumps(list, ensure_ascii=False)


def getdata(id='', address='', arrange='', plot='', language='', year='', limit=''):
    session = HTMLSession()
    url = "https://www.freeok.vip/vodshow/{0}-{1}-{2}-{3}-{4}----{6}---{5}.html".format(id, address, plot, arrange, language, year,limit)
    h = session.get(url=url)
    pattern = 'original.*?referrerpolicy'
    data = re.findall(pattern, h.html.html)
    patternone = 'note.*?div'
    patterntwo = '"/voddetail.*?title'
    dataone = re.findall(patternone, h.html.html)
    datatwo = re.findall(patterntwo, h.html.html)
    list = []
    l = []
    t = []
    # 处理数据，通过正则找出三个数据，然后添加到字典里面
    for item in data:
        datatext = item[0:-16].replace("=", ":")
        datatext = datatext.replace("original", '"img"')
        datatext = datatext.replace("alt", '"name"')
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
        dataname = dict(zip(["icon"], l))
        idname = dict(zip(["gethtml"], t))
        sum = dict(dataname,**datajson)
        list.append(dict(idname, **sum))
    # list = dict(zip(["data"], [list]))
    return json.dumps(list, ensure_ascii=False)


if __name__ == '__main__':
    # getdata()
    # getvip(1)
    # setvip()
    print(setvip(3))
    print(getdata())



