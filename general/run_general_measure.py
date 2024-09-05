from flask import Flask
import threading

from general_measure import Measure
import config


app = Flask(__name__)


# flag = {'end':False, 'data':[], 'id':None}

        




   
data = {'data': Measure(config.nic_name), 'is_started': False}


@app.route('/start/')
def start():
    if not data['is_started']:
        m = data['data']
        m.init()

        p = threading.Thread(target=m.task)  #! 此处只能用Thread不能用Process，因为新的进程就是额外一套资源，不共享变量
        p.start()
    else:
        data['is_started'] = False

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

    #启动后就开始写入数据
    m = data['data']
    m.init()
    p = threading.Thread(target=m.task)  #! 此处只能用Thread不能用Process，因为新的进程就是额外一套资源，不共享变量
    p.start()
    data['is_started'] = True
    try:
        app.run('0.0.0.0', port=10800)
    except KeyboardInterrupt:
        data['data'].write_data()
        print('data has been written back, end!')