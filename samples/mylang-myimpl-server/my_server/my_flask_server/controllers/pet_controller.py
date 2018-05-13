import json

from flask import Blueprint
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request

from flask_server import util

pet_api = Blueprint('pet', __name__)


@pet_api.route('/pet/findByTags', methods=['get'])
def findPetsByTags(tags):
    return '/pet/findByTags GET'


@pet_api.route('/pet/<petId>/uploadImage', methods=['post'])
def uploadFile(petId):
    if not request.json:
        abort(400)
    return '/pet/<petId>/uploadImage POST'


@pet_api.route('/pet/findByStatus', methods=['get'])
def findPetsByStatus(status):
    return '/pet/findByStatus GET'


@pet_api.route('/pet/<petId>', methods=['get'])
def getPetById(petId):
    return '/pet/<petId> GET'


@pet_api.route('/pet/<petId>', methods=['post'])
def updatePetWithForm(petId):
    if not request.json:
        abort(400)
    return '/pet/<petId> POST'


@pet_api.route('/pet/<petId>', methods=['delete'])
def deletePet(api_key, petId):
    return '/pet/<petId> DELETE'


@pet_api.route('/pet', methods=['put'])
def updatePet():
    return '/pet PUT'


@pet_api.route('/pet', methods=['post'])
def addPet():
    if not request.json:
        abort(400)
    return '/pet POST'
