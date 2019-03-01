import os
from flask import Flask, redirect, url_for, request, jsonify, Response, send_file, send_from_directory
from pymongo import MongoClient, ReturnDocument
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
        doc['url'] = f"{request.url_root}img/{doc['uuid']}"
        photos.append(doc)
        
    return jsonify(photos),200

@app.route('/photos/<photo_id>', methods=['GET'])
def get(photo_id):
    doc = db.photos.find_one({"uuid":photo_id})

    if doc is None:
        return jsonify({}), 404
    else:
        doc.pop('_id')
        doc['url'] = f"{request.url_root}img/{doc['uuid']}"
        return jsonify(doc), 200


@app.route('/photos/<photo_id>', methods=['PATCH'])
def update(photo_id):

    data = request.get_json()
    
    changes = {}
    if 'title' in data:
        changes['title'] = data['title'] 
    if 'description' in data:
        changes['description'] = data['description']

    doc = db.photos.find_one_and_update(
        {"uuid":photo_id},
        { "$set": changes ,},
        return_document=ReturnDocument.AFTER
    )

    if doc is None:
        return jsonify({}), 404
    else:
        doc.pop('_id')
        doc['url'] = f"{request.url_root}img/{doc['uuid']}"
        return jsonify(doc), 200

@app.route('/photos', methods=['POST'])
def create():

    data = request.get_json()
    if 'title' not in data:
        return jsonify({"msg":"title is necessary"}),400
    if 'description' not in data:
        return jsonify({"msg":"description is necessary"}),400
    if 'base64' not in data:
        return jsonify({"msg":"base64 is necessary"}),400

    doc = {
        'uuid': uuid.uuid4().hex,
        'title' : data['title'] ,
        'description' : data['description'],
        'base64' : data['base64']
    }
    db.photos.insert_one(doc)
    doc.pop('_id')
    doc['url'] = f"{request.url_root}img/{doc['uuid']}"

    imgdata = base64.b64decode(doc['base64'].split(",")[1])
    filename = doc['uuid'] + '.jpeg'
    with open( './tmp/' + filename, 'wb') as f:
        f.write(imgdata)

    # base64 to img

    # store img to S3

    return jsonify(doc), 201

@app.route('/photos/<photo_id>', methods=['DELETE'])
def delete(photo_id):
    doc = db.photos.find_one_and_delete({"uuid":photo_id})
    if doc is None:
        return jsonify({}), 404
    else:
        doc.pop('_id')
        return jsonify(doc), 200


@app.route('/img/<photo_id>', methods=['GET'])
def img(photo_id):

    doc = db.photos.find_one({"uuid":photo_id})
    return send_from_directory( 
        './tmp',
        filename=doc['uuid'] + '.jpeg', 
        mimetype="image/jpeg")


    # get from S3

    # return send_file( doc['base64'].split(',')[1], mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)