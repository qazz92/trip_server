from flask import Flask, json, Response
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'boo_npe'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ekfqlc152!'
app.config['MYSQL_DATABASE_DB'] = 'boo'
app.config['MYSQL_DATABASE_HOST'] = 'dongaboomin.xyz'
mysql.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/list')
def list():
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * FROM normal_users")
    lists = cursor.fetchall()
    js = json.dumps({'result_body': lists})
    resp = Response(js, status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
