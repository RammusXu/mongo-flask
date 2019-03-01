import os
from flask import Flask, redirect, url_for, request, jsonify, Response, send_file
from pymongo import MongoClient
from bson.json_util import dumps
import json
import uuid
import base64

app = Flask(__name__)

client = MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.photos


@app.route('/')
def show():
    photos = []

    for doc in db.photos.find():
        doc.pop('_id') 
        photos.append(doc)
        
    return jsonify(photos),200
    # _items = db.photos.find()
    # items = [item for item in _items]
    # return dumps(items), 200

@app.route('/photos/<photo_id>', methods=['GET'])
def get(photo_id):
    doc = db.photos.find_one({"uuid":photo_id})
    doc.pop('_id')

    return jsonify(doc), 200


@app.route('/photos/<photo_id>', methods=['PATCH'])
def update(photo_id):

    data = request.get_json()
    name = data['name']
    description = data['description']

    doc = db.photos.find_one({"uuid":photo_id})
    doc.pop('_id')
    if name:
        doc['name'] = description

    if description:
        doc['description'] = description

    doc.save()
    return jsonify(doc), 200

@app.route('/photos', methods=['POST'])
def create():

    item_doc = {
        'uuid': uuid.uuid4().hex,
        'name': request.form['name'],
        'description': request.form['description'],
        'base64': request.form['base64']
    }
    db.photos.insert_one(item_doc)
    item_doc.pop('_id')

    # base64 to img

    # store img to S3

    return jsonify(item_doc), 201

@app.route('/img/<photo_id>', methods=['GET'])
def img(photo_id):
    # get from S3

    # return send_file( doc['base64'].split(',')[1], mimetype="image/jpeg")
    # return send_file( s3file, mimetype="image/jpeg")
    return "TODO"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)