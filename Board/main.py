#-- coding:utf-8 --#
from flask import Flask, request, g, render_template, session, redirect, url_for
from flask import send_from_directory
import sqlite3
import hashlib
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from time import strftime


UPLOAD_FOLDER = './fileupload/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

DATABASE = './db/user.db'
DB = './db/board.db'
REPLYDB = './db/reply.db'
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmNjLWX/,?RT'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

##  DATABASE  ################################################################

def get_db():
    db = getattr(g, 'g_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_bdb():
    bdb = getattr(g, 'b_database', None)
    if bdb is None:
        bdb = g._database = sqlite3.connect(DB)
    return bdb

def get_rdb():
    rdb = getattr(g, 'r_database', None)
    if rdb is None:
        rdb = g._database = sqlite3.connect(REPLYDB)
    return rdb

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    bdb = getattr(g, '_database', None)
    rdb = getattr(g, '_database', None)
    if db is not None:
        return db.close()
    elif bdb is not None:
        return bdb.close()
    elif rdb is not None:
        return rdb.close()

def init_db():
    with app.app_context():
        db = get_db()
        f = open('schema_user.sql','r')
        db.execute(f.read())
        db.commit()
        #with app.open_resource('schema.sql', mode='r') as f:
        #    db.cur
def init_bdb():
    with app.app_context():
        bdb = get_bdb()
        ff = open('schema_board.sql','r')
        bdb.execute(ff.read())
        bdb.commit()

def init_rdb():
    with app.app_context():
        rdb = get_rdb()
        f = open('schema_reply.sql','r')
        rdb.execute(f.read())
        rdb.commit()

def add_user(user_id='jjh', user_pw='123', user_email='jjh@naver.com', user_phone="01012345678"):
    hash_pw = hashlib.sha224(b"user_pw").hexdigest()
    sql = "INSERT INTO accounts (user_id, user_pw, user_email, user_phone) VALUES ('%s', '%s', '%s', '%s')" % (user_id, hash_pw , user_email, user_phone)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def find_user(user_id,user_pw):
    hash_pw = hashlib.sha224(b"user_pw").hexdigest()
    sql = "SELECT user_id, user_pw FROM accounts WHERE user_id='{}' and user_pw='{}'".format(user_id, hash_pw)
    db = get_db()
    res = db.execute(sql)
    res = res.fetchone()
    if res is None:
        return False
    else :
        return True
"""
def time():
    time = datetime.today().strftime('%Y-%m-%d')
    hour = datetime.today().hour
    minute = datetime.today().minute
    if 0<=hour<12:
        hour = hour+16
        h="{}:{}".format(hour,minute)
        time = time+" "+h
        return time
    elif 12<=hour<24:
        hour = hour+4
        h="{}:{}".format(hour,minute)
        time = time+" "+h
        return time
"""
def add_board(title='test', data='test', pw='123'):
    session_writer = session['user_id']
    print session_writer
    time = datetime.today().strftime('%Y-%m-%d')
    hour = datetime.today().hour
    minute = datetime.today().minute
    print (hour, minute)
    print (type(hour), type(minute))
    if 0<=hour<12:
        hour = hour+16
        h = "{}:{}".format(hour, minute)
        time = time+" "+h
        print time
        print type(time)
        sql = "INSERT INTO board (title, data, writer, pw, time) VALUES ('%s', '%s', '%s', '%s', '%s')" % (title, data, session_writer, pw, time)
        bdb = get_bdb()
        bdb.execute(sql)
        res = bdb.commit()
        return res

    elif 12<=hour<24:
        hour = hour+4
        h="{}:{}".format(hour,minute)
        time = time+" "+h
        sql = "INSERT INTO board (title, data, writer, pw, time) VALUES ('%s', '%s', '%s', '%s', '%s')" % (title, data, session_writer, pw, time)
        bdb = get_bdb()
        bdb.execute(sql)
        res = bdb.commit()
        return res


   # print ("HOUR")
    #print hour
    #h = "{}:{}".format(hour, minute)
    #print h
    #sql = "INSERT INTO board (title, data, writer, pw, time) VALUES ('%s', '%s', '%s', '%s', '%s')" % (title, data, session_writer, pw, time)
    #bdb = get_bdb()
    #bdb.execute(sql)
    #res = bdb.commit()
    #return res

def add_comment(idx=0, title='test', data='reply'):
    session_writer = session['user_id']
    hour = datetime.today().hour
    minute = datetime.today().minute
    if 0<=hour<12:
        hour = hour+16
        h="{}:{}".format(hour, minute)
        time = h
        print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        print time
        sql = "INSERT INTO reply (idx, title, data, writer, time) VALUES (%d, '%s', '%s', '%s', '%s')" % (idx, title, data, session_writer, time)
        rdb = get_rdb()
        rdb.execute(sql)
        res = rdb.commit()
        return res
    elif 12<=hour<24:
        hour = hour+4
        h="{}:{}".format(hour, minute)
        time = h
        sql = "INSERT INTO reply (idx, title, data, writer, time) VALUES (%d, '%s', '%s', '%s', '%s')" % (idx, title, data, session_writer, time)
        rdb = get_rdb()
        rdb.execute(sql)
        res = rdb.commit()
        return res

##  Login  ###################################################################

@app.route('/')
def index1():
    session.pop('user_id', None)
#    if session.get('user_id',None) != None:
#        return render_template('board.html')
#    else:
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
#    if request.method =='GET':
#        return render_template('login.html')
#    else:
    user_id = request.form.get('user_id')
    user_pw = request.form.get('user_pw')
    print (user_id, user_pw)

    if find_user(user_id, user_pw) ==  True:
        session['user_id'] = user_id
        return redirect(url_for('board'))
    else:
        return """<script>alert("ID가 존재하지 않습니다.");location.href='/new';</script>"""
#        return """<script>alert("wrong!");location.href='/';</script>"""
#            return  render_template('login.html')
#    else :
 #       add_user(user_id=request.form['user_id'], user_pw=request.form['user_pw'],
  #               user_email=request.form['user_email'], user_phone=request.form['user_phone'])
#        session['user_id'] = user_id
#        return render_template('board.html')
#    return ''
@app.route('/new')
def index2():
    return render_template('new_user.html')

@app.route('/new_user', methods=['GET','POST'])
def new():
    add_user(user_id=request.form['new_id'], user_pw=request.form['new_pw'],
             user_email=request.form['new_email'], user_phone=request.form['new_phone'])
    return redirect(url_for('index1'))

##  board  ###################################################################

@app.route('/board', methods=['GET','POST'])
def board():
    body_data1 = session['user_id']
    print body_data1
    sql = "SELECT * FROM board"
    bdb = get_bdb()
    res = bdb.execute(sql)
    tmp = list(res.fetchall())
    print tmp
    return render_template('board.html', body_data=body_data1, body_data2=tmp)

@app.route('/write', methods=['GET'])
def write():
    return render_template('write.html')

@app.route('/add_write', methods=['GET','POST'])
def add_write():
    if request.method=='POST':
        session_writer = session['user_id']
        s1 = request.form['title']
        s2 = request.form['data']
        s3 = request.form['pw']
        add_board(title=s1, data=s2, pw=s3)
        try:
            f = request.files['file']
        except :
            if 'file' not in request.files:
                pass
        else:
            f.save('./fileupload/'+f.filename)

        print (s1, s2, s3)
        return redirect(url_for('board'))

@app.route('/logout', methods=['GET'])
def logout():
    #session.pop('user_id',None)
    return render_template('login.html')

@app.route('/out1', methods=['GET'])
def out1():
    return render_template('out.html')
@app.route('/out2', methods=['POST'])
def out2():
    d1 = request.form['out_id']
    d2 = request.form['out_pw']
    print d1
    if find_user(d1, d2) == True:
        sql = "DELETE FROM accounts WHERE user_id = '{}'".format(d1)
        db = get_db()
        db.execute(sql)
        res = db.commit()
        return render_template('login.html')
    else :
         return """<script>alert("존재하지 않는 ID입니다..");location.href='/';</script>"""

@app.route('/delete', methods=['GET'])
def delete():
    return """<script>alert("게시물 삭제를 누르셨습니다.");location.href='/delete_pass';</script>"""
@app.route('/delete_pass', methods=['GET'])
def delete_pass():
    return render_template('board_delete.html')
@app.route('/board_delete', methods=['POST'])
def board_delete():
    PW = request.form['pw']
    sql = "SELECT * FROM board WHERE PW ='{}'".format(PW)
    bdb = get_bdb()
    res = bdb.execute(sql)
    tmp = list(res.fetchall())
    print "PW에 해당하는 게시물은"+ str(tmp)
    name = session['user_id']
    num = request.form['num']
    inum = int(num)

    for i in tmp:
        print (name, type(name))
        print (i[3], type(i[3]))
        if (inum == i[0]) and (name==i[3]) and (PW == i[4]):
            sql1 = "DELETE FROM board WHERE IDX='{}'".format(inum)
            sql2 = "UPDATE board SET IDX=IDX-1 WHERE IDX>'{}'".format(inum)
            bdb = get_bdb()
            bdb.execute(sql1)
            bdb.execute(sql2)
            res = bdb.commit()
            return redirect(url_for('board'))
    return """<script>alert("삭제할 수 없습니다..");location.href='/board';</script>"""

@app.route('/modify',methods=['GET'])
def modify():
    return  """<script>alert("게시물 수정을 누르셨습니다.");location.href='/modify_pass';</script>"""
@app.route('/modify_pass', methods=['GET'])
def modify_pass():
    return render_template('board_modify.html')
@app.route('/board_modify',methods=['POST'])
def board_modify():
    PW = request.form['pw']
    sql = "SELECT * FROM board WHERE PW='{}'".format(PW)
    bdb = get_bdb()
    res = bdb.execute(sql)
    tmp = list(res.fetchall())

    name = session['user_id']
    num = request.form['num']
    inum = int(num)

    title = request.form['title']
    data = request.form['data']
    for i in tmp:
        print (str(title), str(data), inum)
        print (type(title), type(data), type(inum))
        if (inum == i[0]) and (name == i[3]) and (PW == i[4]):
            sql = "UPDATE board SET title='{}', data='{}' WHERE IDX='{}'".format(title, data, inum)
            bdb = get_bdb()
            bdb.execute(sql)
            res = bdb.commit()
            return redirect(url_for('board'))
    return """<script>alert("수정할 수 없습니다..");location.href='/board';</script>"""

def allowed_file(filename):
        return '.' in filename and \
                       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def find_reply(idx):
    print("FIND_REPLAY DEF")
    print(idx)
    sql = "select * from reply where idx = '{}'".format(idx)
    rdb = get_rdb()
    res = rdb.execute(sql)
    res = res.fetchall()
    return res

@app.route('/data',methods=['GET'])
def data(idx=''):
    if idx == "":
        idx = request.args.get('idx')
    else:
        idx = idx

    sql1 = "SELECT * FROM board WHERE idx = '{}'".format(idx)
    bdb = get_bdb()
    res1 = bdb.execute(sql1)
    tmp1 = list(res1.fetchall())

    l1 = []
    for i in tmp1:
        for j in i:
            l1.append(j)

    tmp2 = list(find_reply(idx))
    print tmp2

    return render_template('data.html',body_data1=l1, body_data2=tmp2)

@app.route('/reply', methods=['POST'])
def reply_write():
    reply = request.form['data']
    title = request.form['title']
    idx = request.form['idx']
    idx = (int(idx))
    print ("#########################")
    print (idx, type(idx), title, reply)
    print ("#########################")
    add_comment(idx, title, reply)
    body_data1 = session['user_id']
    print body_data1
    sql = "SELECT * FROM board"
    bdb = get_bdb()
    res = bdb.execute(sql)
    tmp = list(res.fetchall())
    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaa"
    print tmp

    return redirect(url_for('data', idx=tmp[0][0] ))

@app.route('/reply_modify', methods=['GET'])
def reply_modify():
    num = request.args.get('num')
    print ("************************************")
    name = session['user_id']
    print (type(num), name)
    num = int(num)
    sql = "SELECT writer FROM reply WHERE num = '{}'".format(num)
    rdb = get_rdb()
    res = rdb.execute(sql)
    tmp = list(res.fetchall())
    val = str(tmp[0][0])
    name = str(name)
    print (tmp[0][0], name)
    print (str(tmp[0][0]), (str(name)))
    if val == name:
        return render_template('reply_modify.html', value = num)
    else:
        return  """<script>alert("수정할 수 없습니다..");location.href='/board';</script>"""

@app.route('/reply_modify2', methods=['POST'])
def reply_modify2():
    data = request.form['data']
    num = request.form['num']
    print (num, data)
    print (type(num), type(data))
    sql = "UPDATE reply SET data='{}' WHERE num='{}'".format(data, num)
    rdb = get_rdb()
    res = rdb.execute(sql)
    res = rdb.commit()
    return redirect(url_for('board'))

@app.route('/reply_delete', methods=['GET'])
def reply_delete():
    name = session['user_id']
    name = str(name)
    num = request.args.get('numb')
    sql = "SELECT writer FROM reply WHERE num = '{}'".format(num)
    rdb = get_rdb()
    res = rdb.execute(sql)
    tmp = list(res.fetchall())
    val = str(tmp[0][0])

    if val == name:
        sql1 = "DELETE FROM reply WHERE num = '{}'".format(num)
        sql2 = "UPDATE reply SET num=num-1 WHERE num>'{}'".format(num)
        rdb = get_rdb()
        res = rdb.execute(sql1)
        res = rdb.execute(sql2)
        res = rdb.commit()
        return redirect(url_for('board'))
    else:
        return """<script>alert("삭제할 수 없습니다..");location.href='/board';</script>"""



##  main  ####################################################################

if __name__ == '__main__':
    #init_db()
    #init_bdb()
    #init_rdb()
    app.run(debug=True, host='0.0.0.0',port=3333)

