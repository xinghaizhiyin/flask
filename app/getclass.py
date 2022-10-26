import sqlite3
import re
import requests
from flask import request
import json
from requests_html import HTMLSession


def getvip(id, address= '',arrange='',plot='',language='',year='',limit=''):
    session = HTMLSession()
    url = "https://www.freeok.vip/vodshow/{0}-{1}-{2}-{3}-{4}----{6}---{5}.html".format(id, address, plot, arrange, language, year,limit)
    h = session.get(url=url)
    pattern = 'original.*?referrerpolicy'
    data = re.findall(pattern, h.html.html)
    patternone = 'note.*?div'
    patterntwo = '"/voddetail.*?title'
    dataone = re.findall(patternone, h.html.html)
    datatwo = re.findall(patterntwo, h.html.html)
    id = 0
    cx = sqlite3.connect("test.db")
    # 删除表
    # cx.execute('''
    # DROP TABLE class;
    # ''')
    # 创建表
    # cx.execute('''
    # create table class(
    # img char(200),
    # name char(100),
    # icon char(100)
    # );''')
    list = []
    listone = []
    listtwo = []
    cx.execute('Delete From class')
    # 获取图片和名称，并写入数据库
    for item in data:
        datatext = item[0:-16].replace("=", ":")
        datatext = datatext.replace("original", '"original"')
        datatext = datatext.replace("alt", '"alt"')
        datatext = datatext.replace(" ", ',')
        datatext = "{" + datatext + "}"
        datajson = json.loads(datatext)
        list.append(datajson)
    # 获取影片记录，1080p，hd
    for itemone in dataone:
        name = dict(zip(["name"], [itemone[6:-5]]))
        listone.append(name)
    # 获取跳转播放连接
    for itemtwo in datatwo:
        icon = dict(zip(["icon"], [itemtwo[1:-7]]))
        listtwo.append(icon)
    listsum = zip(list,listone,listtwo)
    for item,item1,item2 in listsum:
        # 插入数据
        # sql = 'insert into class(id,img,name, icon) values("%s","%s","%s")' % (item, item1, item2)
        # 更新数据，有更新则替换，无则不需替换
        sql = 'replace into class(img,name, icon) values("%s","%s","%s")' % (item, item1, item2)
        # 删除数据
        # sql = 'Delete From class'
        cx.execute(sql)
        # cx.commit()
    cursor = cx.execute("select * from class")
    # 查询数据
    listdata = []
    for row in cursor:
        listdata.append(row)
    listdata = dict(zip(["data"], [listdata]))
    return json.dumps(listdata, ensure_ascii=False)

def setvip():
    cx = sqlite3.connect("test.db")
    cursor = cx.execute("select * from class")
    # 查询数据
    list = []
    for row in cursor:
        list.append(row)
    list = dict(zip(["data"], [list]))
    return json.dumps(list, ensure_ascii=False)


def getdata(id=1, address= '',arrange='',plot='',language='',year='',limit=''):
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
    # getdata()
    getvip(id=1)
    # setvip()
    print(getvip(id=1))



