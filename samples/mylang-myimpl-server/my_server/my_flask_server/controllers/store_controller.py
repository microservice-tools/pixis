import json

from flask import Blueprint
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request

from flask_server import util

store_api = Blueprint('store', __name__)


@store_api.route('/store/order/<orderId>', methods=['get'])
def getOrderById(orderId):
    return '/store/order/<orderId> GET'


@store_api.route('/store/order/<orderId>', methods=['delete'])
def deleteOrder(orderId):
    return '/store/order/<orderId> DELETE'


@store_api.route('/store/inventory', methods=['get'])
def getInventory():
    return '/store/inventory GET'


@store_api.route('/store/order', methods=['post'])
def placeOrder():
    if not request.json:
        abort(400)
    return '/store/order POST'
