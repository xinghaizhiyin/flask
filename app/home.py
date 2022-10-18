from flask import Flask
import data
import datetime
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


if __name__ == '__main__':
    app.config.from_object(Config())
    home = APScheduler()
    home.init_app(app)
    home.start()
    print(111)

    app.run(debug=True)
