import flask
import time
from os.path import splitext
import os.path
from flask import Flask, json, Response, request, jsonify, send_from_directory, render_template
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename

from print import Print
from werkzeug.security import generate_password_hash, \
    check_password_hash

mysql = MySQL()
app = Flask(__name__, static_folder="./public", static_path='')

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'npe'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Alsrb12#$'
app.config['MYSQL_DATABASE_DB'] = 'trip'
app.config['MYSQL_DATABASE_HOST'] = '45.77.31.224'
mysql.init_app(app)

upload_folder = "/Users/qazz92/pythonProject/public"


# upload_folder = "C:\\Users\JRokH\Documents\\trip_server\\public\\"


@app.route('/')
def hello_world():
    return 'Hello World!'


# 회원가입
@app.route('/reg', methods=['POST'])
def reg():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        _email = request.form['email']
        _pw = request.form['pw']

        params = {
            '_email': _email,
            '_pw': generate_password_hash(_pw)
        }

        query = """insert into users (email, pw) 
                 values (%(_email)s, %(_pw)s)"""
        cursor.execute(query, params)
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


@app.route('/sns/list/<path:page>', methods=['GET'])
def getlist(page):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        i_page = int(page)
        query = """SELECT sns_contents.id,
                  sns_contents.post,
                  users.nickname,
                  users.email,
                  (SELECT group_concat(concat(img_path)) FROM sns_imgs WHERE sns_contents.id=sns_imgs.content_id) as imgs,
                  ifnull((SELECT group_concat(concat(users.nickname)) FROM sns_like JOIN users ON sns_like.user_id = users.id WHERE sns_like.content_id=sns_contents.id),'none') as like_user,
                  ifnull((SELECT sns_like.id FROM sns_like WHERE sns_like.user_id=9 and sns_like.content_id=sns_contents.id),0) as like_id,
                  (SELECT count(*) FROM trip.sns_like WHERE content_id=sns_contents.id) as like_count,
                  (SELECT count(*) FROM sns_comment WHERE content_id=sns_contents.id) as comment_count,
                   DATE_FORMAT(sns_contents.updated_at, '%%Y/%%c/%%e %%T') as updated_at
                FROM sns_contents JOIN users ON sns_contents.user_id = users.id
                ORDER BY sns_contents.updated_at DESC LIMIT 10 OFFSET %s"""
        if i_page == 1:
            cursor.execute(query, 0)
        else:
            cursor.execute(query, (i_page + 1) * (i_page + 1) + (i_page + 1))
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

        params_contents = {
            '_post': _post,
            '_user_id': int(_user_id)
        }

        query_contents = """INSERT INTO sns_contents (post, user_id) 
                    VALUES (%(_post)s,%(_user_id)s)"""
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
def send_mail():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        query = """select con.contents, con.want_date, con.user_id, group_concat(img.img_path SEPARATOR ',') as img, group_concat(toge.email SEPARATOR ',') as email
                    from (capsule con LEFT JOIN capsule_imgs img on con.id = img.capsule_id)
                    LEFT JOIN capsule_together toge on con.id = toge.capsule_id
                    WHERE con.id = 21
                    GROUP BY con.id"""
        cursor.execute(query)
        capsule_db = cursor.fetchall()
        # Message(보내는 제목, 보내는사람 이메일, 받는사람 이메일)

        for mails in capsule_db:
            mail_arr = mails[4].split(',')
            for mail in mail_arr:
                Print.print_str(mail)
        # msg = Message("Hello",
        #
        #               sender="npe.dongauniv@gmail.com",
        #
        #               recipients=["rhfoqkq000@naver.com"])
        #
        # # with app.open_resource("statics/img/image.jpg") as fp:
        #
        # #    msg.attach("image.jpg", "image/jpg", fp.read())
        #
        #
        #
        # with app.app_context():
        #
        #     # 메일 내용 보내기
        #
        #     # msg.body = "Hello, World!"
        #
        #     # 메일 템플릿
        #
        #     msg.html = render_template("mailTemplate.html")
        #
        #     # 메일 사진 보내기
        #
        #     with app.open_resource("statics/img/me.jpg") as fp:
        #
        #         msg.attach("me.jpg", "image/jpg", fp.read())
        #
        #     mail.send(msg)
        #
        # # return app.logger.info('메일 성공!')
        js = json.dumps({'result_code': 200, 'result_body': capsule_db})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    except Exception as e:
        return app.logger.error(e)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.debug = True
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        Print.print_str("start!")
    app.run(host='0.0.0.0')
