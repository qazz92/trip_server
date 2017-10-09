from flask import Flask, json, Response, request
from flaskext.mysql import MySQL
from print import Print
from werkzeug.security import generate_password_hash, \
    check_password_hash

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'npe'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Alsrb12#$'
app.config['MYSQL_DATABASE_DB'] = 'trip'
app.config['MYSQL_DATABASE_HOST'] = '45.77.31.224'
mysql.init_app(app)


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
            js = json.dumps({'result_code': 200, 'result_body': 'true'})
        else:
            js = json.dumps({'result_code': 200, 'result_body': 'false'})

        resp = Response(js, status=200, mimetype='application/json')

        return resp

    except Exception as e:
        js = json.dumps({'result_code': 500, 'result_body': str(e)})
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
