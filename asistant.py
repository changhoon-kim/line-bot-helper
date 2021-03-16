# -*- coding: utf8 -*-

from flask import Flask
from flask import request
from flask_restplus import Api, Resource
from flask_restplus import fields

from kazoo.client import KazooClient

import argparse, json
import requests
from werkzeug.wrappers import Request
from io import BytesIO

from logset import *

class LoggerMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        #request = Request(environ, shallow=True)
        #print request.headers
        #print request.data
        #print request.form
        #print request.args

        request = environ['werkzeug.request']
        #print request.headers
        log_data = str(request)
        log_data = log_data.replace('\n', '')

        method = environ['REQUEST_METHOD']
        if method == 'GET':
            if len(request.args):
                log_data = ' '.join([log_data, str(request.args)])
        elif method == 'POST':
            length = int(environ.get('CONTENT_LENGTH') or 0)
            body = environ['wsgi.input'].read(length)
            environ['wsgi.input'] = BytesIO(body)
            if len(body):
                body = body.replace('\n', '')
                log_data = ' '.join([log_data, body])

        access_logger.access(log_data)

        return self.app(environ, start_response)


app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.wsgi_app = LoggerMiddleware(app.wsgi_app)

api = Api(app,
          version='1.0',
          title='Gateway helper',
          description='Gateway support APIs',
          doc='/')

to_line = api.namespace('toLINE', description='To LINE APIs')
from_addr = api.namespace('internal/addr', description='From Addr APIs')

#TODO: check parser param
# https://flask-restplus.readthedocs.io/en/stable/api.html
parser = api.parser()

#TODO: make model file
line_header_fields = api.model('LineHeaderModel', {
    'botId': fields.String(description='Caller LINE bot id', required=True),
})

get_line_profile_model = api.model('GetLineProfileModel', {
    'uuid': fields.Integer(description='uuid', required=True),
})

update_line_profile_model = api.model('UpdateLineProfileModel', {
    'uuid': fields.Integer(description='uuid', required=True),
    'introduction': fields.String(description='introduction', required=True),
    'tel': fields.String(description='tel', required=True),
    'webSiteList': fields.List(fields.String, description='webSite', required=True),
})

def get_access_token():
    token, _ = zk.get(app.config['ZOOKEEPER_PATH'])
    return token

def line_call(url, bot_id):
    access_token = get_access_token()

    headers = {
        'Content-type': 'application/json; charset=UTF-8',
        'X-Line-Bot-Id': bot_id,
        'Authorization': 'Bearer %s' %(access_token),
    }

    r = requests.get(url, headers=headers)

    return r

def get_line_room_type_by_prefix(room_id):
    if room_id.startswith('R'):
        return 'room'
    return 'group'

@to_line.route('/line/user/<string:mid>')
@to_line.doc(params={'mid': 'LINE user mid'})
class LineUser(Resource):
    @to_line.doc(body=line_header_fields)
    def post(self, mid):
        bot_id = json.loads(request.data)['botId']
        url = app.config['LINE_USER_PROFILE'] + mid

        return line_call(url, bot_id).json()

@to_line.route('/line/bot/<string:bot_id>')
@to_line.doc(params={'bot_id': 'LINE bot id'})
class LineBot(Resource):
    def get(self, bot_id):
        url = app.config['LINE_BOT_PROFILE']

        return line_call(url, bot_id).json()

@to_line.route('/line/room/members/<string:room_id>')
@to_line.doc(params={'room_id': 'LINE room id'})
class LineRoomMembers(Resource):
    @to_line.doc(body=line_header_fields)
    def post(self, room_id):
        bot_id = json.loads(request.data)['botId']
        url = app.config['LINE_ROOM_MEMBER'] % (get_line_room_type_by_prefix(room_id), room_id)

        return line_call(url, bot_id).json()

@to_line.route('/line/group/summary/<string:group_id>')
@to_line.doc(params={'group_id': 'LINE group id'})
class LineGroupSummary(Resource):
    @to_line.doc(body=line_header_fields)
    def post(self, group_id):
        bot_id = json.loads(request.data)['botId']
        url = app.config['LINE_GROUP_SUMMARY'] %(group_id)

        return line_call(url, bot_id).json()

@from_addr.route('/getLineProfile')
class AddrGetLineProfile(Resource):
    @from_addr.doc(body=get_line_profile_model)
    def post(self):
        path = request.path
        uuid = json.loads(request.data)['uuid']

        res = path + '?' + str(uuid)
        return res

@from_addr.route('/updateLineProfile')
class AddrUpdateLineProfile(Resource):
    @from_addr.doc(body=update_line_profile_model)
    def post(self):
        path = request.path
        uuid = json.loads(request.data)['uuid']

        res = path + '?' + str(uuid)
        return res

def parseArgs():
    parser = argparse.ArgumentParser(description='asistant', add_help=False)

    parser.add_argument('-?', '--help', action='help')
    parser.add_argument('--conf', required=True, type=str, help='configure')

    return parser.parse_args()

if __name__ == '__main__':
    args = parseArgs()

    app.config.from_pyfile(args.conf)

    zk = KazooClient(hosts=app.config['ZOOKEEPER'])
    zk.start()

    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)

    zk.stop()


#TODO
# 1. python venv 구성
# 2. python requirement 추가 (flask, flask_restplus, kazoo)
