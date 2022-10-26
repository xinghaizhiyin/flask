import json

from flask import Flask,request,redirect
import data, getclass
from flask_apscheduler import APScheduler
app = Flask(__name__)


# 定时任务
class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'home:data.getdata',
            'trigger': 'cron',
            'day': '*',
            'hour': '22',
            'minute': '33',
            'second': '20'
        },
        {
            'id': 'job2',
            'func': 'home:getclass.getsum',
            'trigger': 'cron',
            'day': '*',
            'hour': '3',
            'minute': '16',
            'second': '20'
        }
    ]
    SCHEDULER_API_ENABLED = True


@app.route('/home', methods=['get'])
def hello_world():
    return data.setdata()


@app.route('/films/vip', methods=["GET", 'POST'])
def vip():
    id = int(request.values['id'])  # 类型
    address = request.values['address']  # 地区
    arrange = request.values['arrange']  # 类型
    plot = request.values['plot']  # 排行
    language = request.values['language']  # 语言
    year = request.values['year']  # 年份
    limit = request.values['limit']  # 翻页
    if request.method == "POST":
        # if request.content_type.startswith('application/json'):
        #     comment = request.json.get('content')
        # elif request.content_type.startswith('ultipart/for-data'):
        #     comment = request.form.get('content')
        # else:
        # 从数据库取
        if address == '' and arrange == '' and plot == '' and language == '' and year == '' and limit == '1':
            if id == 1 :
                return getclass.setvip(id)
            elif id == 2:
                return getclass.setvip(id)
            elif id == 3:
                return getclass.setvip(id)
        else:
            datajson = getclass.getdata(id, address, arrange, plot, language, year, limit)
            return datajson
    elif request.method == "GET":
        # 从数据库取
        if address == '' and arrange == ''and plot == ''and language == ''and year == ''and limit == '1':
            if id == 1:
                return getclass.setvip(id)
            elif id == 2:
                return getclass.setvip(id)
            elif id == 3:
                return getclass.setvip(id)
        else:
            datajson = getclass.getdata(id, address, arrange, plot, language, year, limit)
            return datajson


if __name__ == '__main__':
    app.config.from_object(Config())
    home = APScheduler()
    home.init_app(app)
    home.start()

    app.run(host='0.0.0.0', port=5001)
