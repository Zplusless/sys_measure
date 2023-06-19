from flask import Flask
import threading

from measure import Measure
import config


app = Flask(__name__)


# flag = {'end':False, 'data':[], 'id':None}

        




   
data = {'data': Measure(config.nic_name)}


@app.route('/start/')
def start():
    m = data['data']
    m.init()

    p = threading.Thread(target=m.task)  #! 此处只能用Thread不能用Process，因为新的进程就是额外一套资源，不共享变量
    p.start()

    return 'start'


@app.route('/insert/<msg>/')
def insert(msg):
    m = data['data']
    m.insert_mark(msg=msg)
    return 'insert'


@app.route('/end/')
def end():
    m = data['data']
    m.end()

    m.write_data()

    return 'end'

if __name__ == "__main__":
    try:
        app.run('0.0.0.0', port=10800)
    except KeyboardInterrupt:
        data['data'].write_data()
        print('data has been written back, end!')