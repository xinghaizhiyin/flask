from flask import Flask,request
import data, getclass
from flask_apscheduler import APScheduler
app = Flask(__name__)


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
        }
    ]
    SCHEDULER_API_ENABLED = True


@app.route('/home', methods=['get'])
def hello_world():
    return data.setdata()


@app.route('/class/vip', methods=["GET",'POST'])
def vip():
    id = request.args['id']  #类型
    address = request.args['address']  #地区
    arrange = request.args['arrange']  #类型
    plot = request.args['plot']  #排行
    language = request.args['language']  #语言
    year = request.args['year']  #年份
    limit = request.args['limit']  #翻页
    jsondata = getclass.getdata(id, address, arrange, plot, language, year, limit)
    return jsondata


if __name__ == '__main__':
    app.config.from_object(Config())
    home = APScheduler()
    home.init_app(app)
    home.start()

    app.run(host='0.0.0.0', port=5001)
