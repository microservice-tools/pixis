import json

from flask import Blueprint
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request

from flask_server import util

user_api = Blueprint('user', __name__)


@user_api.route('/user', methods=['post'])
def createUser():
    if not request.json:
        abort(400)
    return '/user POST'


@user_api.route('/user/<username>', methods=['get'])
def getUserByName(username):
    return '/user/<username> GET'


@user_api.route('/user/<username>', methods=['put'])
def updateUser(username):
    return '/user/<username> PUT'


@user_api.route('/user/<username>', methods=['delete'])
def deleteUser(username):
    return '/user/<username> DELETE'


@user_api.route('/user/createWithList', methods=['post'])
def createUsersWithListInput():
    if not request.json:
        abort(400)
    return '/user/createWithList POST'


@user_api.route('/user/logout', methods=['get'])
def logoutUser():
    return '/user/logout GET'


@user_api.route('/user/login', methods=['get'])
def loginUser(username, password):
    return '/user/login GET'


@user_api.route('/user/createWithArray', methods=['post'])
def createUsersWithArrayInput():
    if not request.json:
        abort(400)
    return '/user/createWithArray POST'
