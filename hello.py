from sched import scheduler

import flask
import time
from os.path import splitext
import os.path
from flask import Flask, json, Response, request, render_template
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename

from print import Print
from werkzeug.security import generate_password_hash, \
    check_password_hash
from werkzeug.contrib.fixers import ProxyFix
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import time

# configuration
SECRET_KEY = 'hidden'
USERNAME = 'secret'
PASSWORD = 'secret'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'npe.dongauniv@gmail.com'
MAIL_PASSWORD = 'Q!2dltnals'

mysql = MySQL()
app = Flask(__name__,template_folder='./templates', static_folder='./public', static_path='')
app.config.from_object(__name__)
mail = Mail(app)
ctx = app.app_context()
ctx.push()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'trip_npe'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Alsrb12#$'
app.config['MYSQL_DATABASE_DB'] = 'trip'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

upload_folder = "/root/trip_server/public"
scheduler = BackgroundScheduler()


# mysql = MySQL()
# app = Flask(__name__, template_folder="./templates", static_folder="./public", static_path='')
# 
# # configuration
# SECRET_KEY = 'hidden'
# USERNAME = 'secret'
# PASSWORD = 'secret'
# 
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 465
# MAIL_USE_TLS = False
# MAIL_USE_SSL = True
# MAIL_USERNAME = 'npe.dongauniv@gmail.com'
# MAIL_PASSWORD = 'Q!2dltnals'
# 
# # MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'trip_npe'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'Alsrb12#$'
# app.config['MYSQL_DATABASE_DB'] = 'trip'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)
# mail = Mail(app)
# 
# # upload_folder = "C:\\Users\JRokH\Documents\\trip_server\\public\\"
# upload_folder = "/root/trip_server/public"
# scheduler = BackgroundScheduler()


# upload_folder = "/Users/qazz92/pythonProject/trip_server/public"


@app.route('/')
def hello_world():
    return 'Hello World!'


# 캡슐
@app.route('/capsule', methods=['POST'])
def capsule():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _contents = flask.request.form['contents']
        _want_date = flask.request.form['want_date']
        _user_id = flask.request.form['user_id']
        _imagefile = flask.request.files.getlist('imagefile')
        _together = flask.request.form.getlist('together')

        Print.print_str(_together)

        params_contents = {
            '_contents': _contents,
            '_want_date': _want_date,
            '_user_id': int(_user_id)
        }

        query_contents = """INSERT INTO capsule (contents, want_date, user_id)
                            VALUES (%(_contents)s,%(_want_date)s,%(_user_id)s)"""

        cursor.execute(query_contents, params_contents)
        capsule_id = conn.insert_id()

        make_folder = upload_folder + "/" + time.strftime("%Y%m%d") + "/" + _user_id

        if os.path.exists(make_folder):
            Print.print_str("있음")
        else:
            Print.print_str("없음")
            os.makedirs(make_folder)
            if os.path.exists(make_folder):
                Print.print_str("없어서 만드는데 성공함")
            else:
                Print.print_str("없어서 만드는 코드를 실행하긴 했는데 확인해보니 사실 없음")

        for i in range(len(_imagefile)):
            filename = secure_filename(_imagefile[i].filename)
            _imagefile[i].save(os.path.join(make_folder, filename))

            params_imgs = {
                'img_path': time.strftime("%Y%m%d") + "/" + _user_id + "/" + filename,
                'img_ext': splitext_(filename)[1],
                'capsule_id': int(capsule_id)
            }

            query_imgs = """insert into capsule_imgs (img_path, img_ext, capsule_id)
                                       values (%(img_path)s, %(img_ext)s, %(capsule_id)s)"""
            cursor.execute(query_imgs, params_imgs)

        for j in range(len(_together)):
            params_together = {
                'email': _together[j],
                'capsule_id': int(capsule_id)
            }

            query_together = """insert into capsule_together (email, capsule_id)
                                                   values (%(email)s, %(capsule_id)s)"""
            cursor.execute(query_together, params_together)

        conn.commit()
        js = json.dumps({'result_code': 200})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        Print.print_str(str(e))
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


# 회원가입
@app.route('/reg', methods=['POST'])
def reg():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _email = request.form['email']
        _nickname = request.form['nickname']
        _image = request.form['image']
        Print.print_str(_email)
        Print.print_str(_nickname)
        Print.print_str(_image)
        params = {
            '_email': _email,
            '_nickname': _nickname
        }

        query = """select id, email from users where email=%(_email)s and nickname=%(_nickname)s"""
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result is None:
            params2 = {
                '_email': _email,
                '_nickname': _nickname,
                '_image': _image
            }
            query2 = """insert into users (email, nickname, image) 
                         values (%(_email)s, %(_nickname)s, %(_image)s)"""
            cursor.execute(query2, params2)
            conn.commit()
            js = json.dumps({'result_code': conn.insert_id()})
            resp = Response(js, status=200, mimetype='application/json')
            return resp

        else:
            Print.print_str(str(result[0]))
            js = json.dumps({'result_code': result[0]})
            resp = Response(js, status=200, mimetype='application/json')
            return resp

    except Exception as e:
        return json.dumps({'error': str(e)})

    finally:
        cursor.close()
        conn.close()


# 로그인
@app.route('/login', methods=['POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _email = request.form['email']
        _pw = request.form['pw']

        # 시스템 프린트 ## 로그아님 주의!
        Print.print_str(_pw)

        query = "select * from users where email = %s"
        cursor.execute(query, _email)

        user_db_info = cursor.fetchone()

        is_true = check_password_hash(user_db_info[2], _pw)

        if is_true:
            js = json.dumps({'result_code': 200, 'result_body': user_db_info})
        else:
            js = json.dumps({'result_code': 201, 'result_body': 'false'})

        resp = Response(js, status=200, mimetype='application/json')

        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route('/hotchu', methods=['GET'])
def get_hotchu_list():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        query = """select id,title,summary,content,img_path,DATE_FORMAT(updated_at, '%Y/%c/%e %T') as updated_at from hotchu"""
        cursor.execute(query)
        # row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        columns = cursor.description
        sns_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


# 해시태그 목록 불러오기
@app.route('/hashtag', methods=['GET'])
def gethashtag():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        query = "SELECT concat('@',nickname) as result FROM users UNION SELECT concat('#',tag) as result FROM sns_hashtag UNION SELECT concat('~',location_alias) as result FROM sns_location"

        cursor.execute(query)

        columns = cursor.description
        sns_tag_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                        cursor.fetchall()]
        Print.print_str(sns_tag_list)
        js = json.dumps({'result_code': 200, 'result_body': sns_tag_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        Print.print_str(str(e))
        return json.dumps({'error': str(e)})

    finally:
        cursor.close()
        conn.close()


@app.route('/sns/<path:user_id>/list/<path:page>', methods=['GET'])
def getlist(user_id, page):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        i_page = int(page)
        i_user_id = int(user_id)

        Print.print_str(i_user_id)

        query = """SELECT sns_contents.id,
                  sns_contents.post,
                  users.nickname,
                  users.email,
                  users.id as user_id,
                  users.image as user_profile,
				  sns_location.location,
                  sns_location.location_alias,
                  (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                  ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                  ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=%s and sns_like.content_id=sns_contents.id),0) as like_id,
                  (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                  (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                   DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                FROM sns_contents JOIN users ON sns_contents.user_id = users.id
	          JOIN sns_location ON sns_location.id=sns_contents.location_id
                ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %s"""
        if i_page == 1:
            cursor.execute(query, (i_user_id, 0))
        else:
            cursor.execute(query, (i_user_id, (i_page + 1) * (i_page + 1) + (i_page + 1)))
        # row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        columns = cursor.description
        sns_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

        # json_data = []
        # for result in sns_list:
        #     json_data.append(dict(zip(row_headers, result)))
        # for idx, result in sns_list:

        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route('/sns/<path:user_id>/list/<path:category>/<path:hashtag>/<path:page>', methods=['GET'])
def getlistforhash(user_id, category, hashtag, page):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        i_page = int(page)
        i_category = int(category)
        i_user_id = int(user_id)

        if 0 == i_category:
            query = """SELECT sns_contents.id,
                          sns_contents.post,
                          users.nickname,
                          users.email,
                          users.id as user_id,
                          users.image as user_profile,
                          sns_location.location,
                          sns_location.location_alias,
                          (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                          ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                          ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=%s and sns_like.content_id=sns_contents.id),0) as like_id,
                          (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                          (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                           DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                        FROM sns_ch JOIN sns_contents ON sns_ch.content_id = sns_contents.id 
                        JOIN users ON sns_contents.user_id = users.id 
                        JOIN sns_location ON sns_location.id=sns_contents.location_id
                        WHERE hash_id = (SELECT id FROM sns_hashtag WHERE tag=%s)
                        ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %s"""
            if i_page == 1:
                cursor.execute(query, (i_user_id, hashtag, 0))
            else:
                cursor.execute(query, (i_user_id, hashtag, (i_page + 1) * (i_page + 1) + (i_page + 1)))
        elif 1 == i_category:
            query = """SELECT sns_contents.id,
                          sns_contents.post,
                          users.nickname,
                          users.email,
                          users.id as user_id,
                        users.image as user_profile,
                  		  sns_location.location,
                          sns_location.location_alias,
                          (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                          ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                          ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=%s and sns_like.content_id=sns_contents.id),0) as like_id,
                          (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                          (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                           DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                        FROM sns_contents JOIN users ON sns_contents.user_id = users.id
                         JOIN sns_location ON sns_location.id=sns_contents.location_id
                    WHERE users.nickname=%s
                        ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %s"""
            if i_page == 1:
                cursor.execute(query, (i_user_id, hashtag, 0))
            else:
                cursor.execute(query, (i_user_id, hashtag, (i_page + 1) * (i_page + 1) + (i_page + 1)))
        else:
            query = """SELECT sns_contents.id,
                          sns_contents.post,
                          users.nickname,
                          users.email,
                          users.id as user_id,
                          users.image as user_profile,
                  		  sns_location.location,
                          sns_location.location_alias,
                          (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                          ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                          ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=%s and sns_like.content_id=sns_contents.id),0) as like_id,
                          (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                          (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                           DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                        FROM sns_contents JOIN users ON sns_contents.user_id = users.id
                        JOIN sns_location ON sns_location.id=sns_contents.location_id
                        WHERE sns_location.location like %s OR sns_location.location_alias LIKE %s
                        ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %s"""
            hashtagSet = '%' + hashtag + '%'
            if i_page == 1:
                cursor.execute(query, (i_user_id, hashtagSet, hashtagSet, 0))
            else:
                cursor.execute(query, (i_user_id, hashtag, hashtagSet, (i_page + 1) * (i_page + 1) + (i_page + 1)))

        # row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        columns = cursor.description
        sns_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

        # json_data = []
        # for result in sns_list:
        #     json_data.append(dict(zip(row_headers, result)))
        # for idx, result in sns_list:

        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


# 지역 검색
@app.route('/location/search', methods=['POST'])
def searchlocation():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _search = request.form['search']

        Print.print_str(_search)

        likeSe = "'%" + _search + "%'"

        query = "select * from sns_location where sns_location.location like " + likeSe + " or sns_location.location_alias like " + likeSe

        cursor.execute(query)

        columns = cursor.description
        sns_location_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                             cursor.fetchall()]
        Print.print_str(sns_location_list)
        js = json.dumps({'result_code': 200, 'result_body': sns_location_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        Print.print_str(str(e))
        return json.dumps({'error': str(e)})

    finally:
        cursor.close()
        conn.close()


# 지역 추가
@app.route('/location/insert', methods=['POST'])
def insertlocation():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _location = request.form['location']
        _location_alias = request.form['location_alias']

        Print.print_str(_location)
        Print.print_str(_location_alias)

        params = {
            '_location': _location,
            '_location_alias': _location_alias,
        }

        selectQuery = """select id, location, location_alias from sns_location where 
                location=%(_location)s AND location_alias=%(_location_alias)s"""
        cursor.execute(selectQuery, params)
        row_count = cursor.rowcount
        if row_count == 0:
            Print.print_str("row====0")
            query = """insert into sns_location (location, location_alias) 
            values (%(_location)s, %(_location_alias)s)"""
            cursor.execute(query, params)
            conn.commit()
        else:
            Print.print_str("row!=0")


        js = json.dumps({'result_code': 200})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        Print.print_str(str(e))
        return json.dumps({'error': str(e)})

    finally:
        cursor.close()
        conn.close()


@app.route('/sns/search/<path:keyword>', methods=['GET'])
def getkeyword(keyword):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        keyword_set = "%" + keyword + "%"
        query = """ SELECT concat('#',tag) as result FROM sns_hashtag WHERE tag LIKE %s UNION
                    SELECT  concat('@',nickname) as result FROM users WHERE nickname LIKE %s
                    """
        cursor.execute(query, (keyword_set, keyword_set))

        # row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        # columns = cursor.description
        # keyword_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        keyword_list = []
        for i in range(cursor.rowcount):
            keyword_list.append(cursor.fetchone()[0])
        # json_data = []
        # for result in sns_list:
        #     json_data.append(dict(zip(row_headers, result)))
        # for idx, result in sns_list:

        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': keyword_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route("/sns/comment/write", methods=['POST'])
def commentwrite():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        _content_id = request.form['content_id']
        _user_id = request.form['user_id']
        _article = request.form['article']

        Print.print_str(_article)

        params_comment = {
            '_content_id': int(_content_id),
            '_user_id': int(_user_id),
            '_article': _article
        }

        query_comment = """INSERT INTO
            sns_comment(user_id, content_id, article)
                    VALUES (%(_user_id)s,%(_content_id)s, %(_article)s)"""
        cursor.execute(query_comment, params_comment)
        query = """SELECT sns_comment.id as id,
            sns_comment.article as article, users.nickname as nickname,
            DATE_FORMAT(sns_comment.updated_at, '%%Y/%%c/%%e %%T') as updated_at
            FROM sns_comment JOIN users ON sns_comment.user_id = users.id WHERE content_id = %s and user_id= %s
            ORDER BY sns_comment.updated_at DESC LIMIT 1"""
        cursor.execute(query, (int(_content_id), int(_user_id)))
        conn.commit()

        columns = cursor.description
        sns_comment_recent_one = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                                  cursor.fetchall()]

        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_comment_recent_one})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        conn.rollback()
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route('/sns/<path:content_id>/comment/<path:page>', methods=['GET'])
def getcommentlist(content_id, page):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        i_content_id = int(content_id)
        i_page = int(page)

        query = """SELECT sns_comment.id as id, 
            sns_comment.article as article, users.nickname as nickname,
            users.image as profile, 
             DATE_FORMAT(sns_comment.updated_at, '%%Y/%%c/%%e %%T') as updated_at  
            FROM sns_comment JOIN users ON sns_comment.user_id = users.id WHERE content_id = %(_content_id)s
            ORDER BY sns_comment.updated_at LIMIT 10 OFFSET %(_page)s"""
        if i_page == 1:
            params = {
                '_content_id': i_content_id,
                '_page': 0
            }
        else:
            params = {
                '_content_id': i_content_id,
                '_page': (i_page + 1) * (i_page + 1) + (i_page + 1)
            }

        cursor.execute(query, params)
        # row_headers = [x[0] for x in cursor.description]  # this will extract row headers
        columns = cursor.description
        sns_comment_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in
                            cursor.fetchall()]

        js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_comment_list})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        conn.rollback()
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


def splitext_(path):
    for ext in ['.tar.gz', '.tar.bz2']:
        if path.endswith(ext):
            return path[:-len(ext)], path[-len(ext):]
    return splitext(path)


@app.route('/sns/write', methods=['POST'])
def write():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _post = request.form.get('post')
        # _imagefile = flask.request.files.getlist('imagefile')
        # _user_id = flask.request.form.get('user_id')
        # _hash_arr = flask.request.form.getlist("hash")
        _imagefile = request.files.getlist('imagefile')
        _user_id = request.form.get('user_id')
        _hash_arr = request.form.getlist("hash")
        _location = request.form.get("location")
        _location_alias = request.form.get("location_alias")

        params_location = {
            '_location': _location,
            '_location_alias': _location_alias,
        }

        query = """insert into sns_location (location, location_alias) 
                 values (%(_location)s, %(_location_alias)s)"""
        cursor.execute(query, params_location)
        _location_id = conn.insert_id()

        params_contents = {
            '_post': _post,
            '_user_id': int(_user_id),
            '_location_id': int(_location_id)
        }

        query_contents = """INSERT INTO sns_contents (post, user_id, location_id) 
                    VALUES (%(_post)s,%(_user_id)s,%(_location_id)s)"""
        cursor.execute(query_contents, params_contents)

        content_id = conn.insert_id()

        _hashtag_arr = []

        for hash_item in _hash_arr:
            cursor.execute("SELECT * FROM sns_hashtag WHERE tag= %s", hash_item)
            exist_tag = cursor.fetchone()

            if exist_tag is not None:
                _hashtag_arr.append(exist_tag[0])
            else:
                cursor.execute("""INSERT INTO sns_hashtag (tag)
                            VALUES (%s)""", hash_item)
                _hashtag_arr.append(conn.insert_id())

        for hash_id in _hashtag_arr:
            params_ch = {
                'content_id': int(content_id),
                'hash_id': int(hash_id)
            }
            query_ch = """INSERT INTO sns_ch (content_id, hash_id) 
                               VALUES (%(content_id)s,%(hash_id)s)"""
            cursor.execute(query_ch, params_ch)

        make_foler = upload_folder + "/" + time.strftime("%Y%m%d") + "/" + _user_id

        if os.path.exists(make_foler):
            Print.print_str("있음")
        else:
            Print.print_str("없음")
            os.makedirs(make_foler)
            if os.path.exists(make_foler):
                Print.print_str("없어서 만드는데 성공함")
            else:
                Print.print_str("없어서 만드는 코드를 실행하긴 했는데 확인해보니 사실 없음")

        for i in range(len(_imagefile)):
            filename = secure_filename(_imagefile[i].filename)
            _imagefile[i].save(os.path.join(make_foler, filename))

            params_imgs = {
                'img_path': time.strftime("%Y%m%d") + "/" + _user_id + "/" + filename,
                'img_ext': splitext_(filename)[1],
                'content_id': content_id,
            }

            query_imgs = """insert into sns_imgs (img_path, img_ext, content_id)
                               values (%(img_path)s, %(img_ext)s, %(content_id)s)"""
            cursor.execute(query_imgs, params_imgs)

        conn.commit()
        js = json.dumps({'result_code': 200, 'result_body': '글을 저장했습니다.'})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        conn.rollback()
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


# @app.route('/sns/write', methods=['POST'])
# def write():
#     conn = mysql.connect()
#     cursor = conn.cursor()
#
#     try:
#         _post = request.form.get('post')
#         # _imagefile = flask.request.files.getlist('imagefile')
#         # _user_id = flask.request.form.get('user_id')
#         # _hash_arr = flask.request.form.getlist("hash")
#         _imagefile = request.files.getlist('imagefile')
#         _user_id = request.form.get('user_id')
#         _hash_arr = request.form.getlist("hash")
#
#         params_contents = {
#             '_post': _post,
#             '_user_id': int(_user_id)
#         }
#
#         query_contents = """INSERT INTO sns_contents (post, user_id)
#                     VALUES (%(_post)s,%(_user_id)s)"""
#         cursor.execute(query_contents, params_contents)
#
#         content_id = conn.insert_id()
#
#         _hashtag_arr = []
#
#         for hash_item in _hash_arr:
#             cursor.execute("SELECT * FROM sns_hashtag WHERE tag= %s", hash_item)
#             exist_tag = cursor.fetchone()
#
#             if exist_tag is not None:
#                 _hashtag_arr.append(exist_tag[0])
#             else:
#                 cursor.execute("""INSERT INTO sns_hashtag (tag)
#                             VALUES (%s)""", hash_item)
#                 _hashtag_arr.append(conn.insert_id())
#
#         for hash_id in _hashtag_arr:
#             params_ch = {
#                 'content_id': int(content_id),
#                 'hash_id': int(hash_id)
#             }
#             query_ch = """INSERT INTO sns_ch (content_id, hash_id)
#                                VALUES (%(content_id)s,%(hash_id)s)"""
#             cursor.execute(query_ch, params_ch)
#
#         make_foler = upload_folder + "/" + time.strftime("%Y%m%d") + "/" + _user_id
#
#         if os.path.exists(make_foler):
#             Print.print_str("있음")
#         else:
#             Print.print_str("없음")
#             os.makedirs(make_foler)
#             if os.path.exists(make_foler):
#                 Print.print_str("없어서 만드는데 성공함")
#             else:
#                 Print.print_str("없어서 만드는 코드를 실행하긴 했는데 확인해보니 사실 없음")
#
#         for i in range(len(_imagefile)):
#             filename = secure_filename(_imagefile[i].filename)
#             _imagefile[i].save(os.path.join(make_foler, filename))
#
#             params_imgs = {
#                 'img_path': time.strftime("%Y%m%d") + "/" + _user_id + "/" + filename,
#                 'img_ext': splitext_(filename)[1],
#                 'content_id': content_id,
#             }
#
#             query_imgs = """insert into sns_imgs (img_path, img_ext, content_id)
#                                values (%(img_path)s, %(img_ext)s, %(content_id)s)"""
#             cursor.execute(query_imgs, params_imgs)
#
#         conn.commit()
#         js = json.dumps({'result_code': 200, 'result_body': '글을 저장했습니다.'})
#         resp = Response(js, status=200, mimetype='application/json')
#         return resp
#
#     except Exception as e:
#         conn.rollback()
#         js = json.dumps({'result_code': 500, 'result_body': str(e)})
#         resp = Response(js, status=200, mimetype='application/json')
#         return resp
#
#     finally:
#         cursor.close()
#         conn.close()

@app.route('/sns/delete/<path:number>', methods=['GET'])
def deleteSns(number):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        query = """delete from trip.sns_contents where id=%s;"""
        cursor.execute(query, number)
        conn.commit()
        js = json.dumps({'result_code': 200})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        Print.print_str(str(e))
        return json.dumps({'error': str(e)})

    finally:
        cursor.close()
        conn.close()


@app.route('/sns/list/like/<path:page>/<path:user_id>', methods=['GET'])
def getlistlike(page, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        i_page = int(page)
        query = """SELECT sns_contents.id,
                 sns_contents.post,
                 users.nickname,
                 users.email,
                 users.id as user_id,
                 users.image as user_profile,
                 sns_location.location,
                 sns_location.location_alias,
                 (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                 ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                 ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=%(_user_id)s and sns_like.content_id=sns_contents.id),0) as like_id,
                 (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                 (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                  DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                  FROM sns_contents JOIN users ON sns_contents.user_id = users.id
                  JOIN sns_location ON sns_location.id=sns_contents.location_id
                  JOIN sns_like ON sns_contents.id = sns_like.content_id WHERE sns_like.user_id=%(_user_id)s
                  ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %(_page)s;"""

        if i_page == 1:
            params = {
                '_page': 0,
                '_user_id': int(user_id),
            }
            cursor.execute(query, params)
        else:
            params = {
                '_page': (i_page + 1) * (i_page + 1) + (i_page + 1),
                '_user_id': int(user_id),
            }
            cursor.execute(query, params)

        columns = cursor.description
        sns_list = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

        if cursor.rowcount is None:
            js = json.dumps({'result_code': 200, 'items_count': 0, 'result_body': sns_list})
        else:
            js = json.dumps({'result_code': 200, 'items_count': cursor.rowcount, 'result_body': sns_list})

        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route("/sns/like", methods=['POST'])
def like():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        _content_id = request.form['content_id']
        _user_id = request.form['user_id']

        params_contents = {
            '_content_id': _content_id,
            '_user_id': int(_user_id)
        }

        query_contents = """INSERT INTO sns_like (content_id, user_id) 
                    VALUES (%(_content_id)s,%(_user_id)s)"""
        cursor.execute(query_contents, params_contents)
        _like_id = conn.insert_id()
        conn.commit()
        js = json.dumps({'result_code': 200, 'result_body': _like_id})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        conn.rollback()
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


@app.route("/sns/unlike", methods=['POST'])
def unlike():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _content_id = request.form['content_id']
        _user_id = request.form['user_id']

        params_unlike = {
            '_content_id': _content_id,
            '_user_id': int(_user_id)
        }

        query_unlike = """DELETE FROM sns_like WHERE content_id = %(_content_id)s AND user_id = %(_user_id)s"""
        cursor.execute(query_unlike, params_unlike)
        conn.commit()
        js = json.dumps({'result_code': 200})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        conn.rollback()
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


# 메일보내기
@app.route('/send_mail', methods=['GET'])
def send_mail(today_content, today_email):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        # for popEmail in todayEmail:
        #     Print.print_str(popEmail)

        _email = today_email[0]

        params_contents = {
            '_email': _email,
        }

        query = """SELECT
                   ifnull((SELECT group_concat(concat(capsule_imgs.img_path)) FROM capsule_imgs WHERE capsule_together.capsule_id=capsule_imgs.capsule_id),'none') as imgs
                   FROM capsule_together WHERE capsule_together.email = %(_email)s"""
        cursor.execute(query, params_contents)
        capsule_db = cursor.fetchall()

        # Message(보내는 제목, 보내는사람 이메일, 받는사람 이메일)
        msg = Message("추억이 도착했습니다. -발자취 드림-",
                      sender="npe.dongauniv@gmail.com",
                      recipients=today_email)

        with app.app_context():
            # 메일 내용 보내기
            msg.body = today_content

            show_image = []

            # 메일 사진 보내기
            if cursor.rowcount == 0:
                Print.print_str("EMPTY")
            else:
                for images in capsule_db:
                    image_arr = images[0].split(',')
                    for img in image_arr:
                        show_image.append(img)
                        with app.open_resource(upload_folder +"/"+ img) as fp:
                            msg.attach(img, "image/jpg", fp.read())

                    # 메일 템플릿
                    host = "http://dongaboomin.xyz:20090/"
                    msg.html = render_template("mailTemplate.html",
                                               img_path=host + show_image[0],
                                               send_contents=today_content)

                    mail.send(msg)

        # return app.logger.info('메일 성공!')
        js = json.dumps({'result_code': 200, 'result_body': capsule_db})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        return app.logger.error(e)

    finally:
        cursor.close()
        conn.close()


# 오늘 메일을 보내야하는 사람 선택하기
@scheduler.scheduled_job('cron', day_of_week='mon-sun', hour=6, minute=0)
@app.route('/select_mail', methods=['GET'])
def select_mail():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        query = """SELECT capsule.contents,
                   ifnull((SELECT group_concat(concat(capsule_together.email)) FROM capsule_together WHERE capsule_together.capsule_id=capsule.id),'none') as like_id
                   FROM capsule WHERE capsule.want_date = CURRENT_DATE """
        cursor.execute(query)
        capsule_db = cursor.fetchall()

        mail_arr = []

        if cursor.rowcount == 0:
            Print.print_str("EMPTY")
        else:
            for popDB in capsule_db:
                db_contents = popDB[0]
                db_mails = popDB[1].split(',')
                for mails in db_mails:
                    Print.print_str(mails)
                    mail_arr.append(mails)

                send_mail(db_contents, mail_arr)

                mail_arr = []

        js = json.dumps({'result_code': 200, 'result_body': capsule_db})
        resp = Response(js, status=200, mimetype='application/json')

        return resp

    except Exception as e:
        return app.logger.error(e)

    finally:
        cursor.close()
        conn.close()


scheduler.start()

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0')
