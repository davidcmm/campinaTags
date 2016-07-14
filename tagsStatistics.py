#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth

import hashlib

import json

auth = HTTPBasicAuth()
app = Flask(__name__)

users = {
    '1': {
        'id': 1,
        'points': 0
    },
    '2': {
        'id': 2,
        'points': 10
    }
}

images = [
    "joao_pessoa": {
        'image': "joao_pessoa",
        'tags': {"verde" : 1, "amplo": 1}
    },
    "odon_bezzerra" : {
        'image': "odon_bezzerra",
        'tags': {"velho" : 1, "sujo": 1}
    }
]

@app.route('/')
def index():
    return "Hello, World!"

def get_users(user_id):
    if not users.has_key(user_id):
	return {}
    return users[user_id]

@app.route('/campinaTags/api/v1.0/users', methods=['GET'])
def get_all_users():
    return jsonify({'users': users})

@app.route('/campinaTags/api/v1.0/users/<int:user_id>', methods=['GET'])
def get_users_per_id(user_id):
    user = get_users(user_id)
    if len(user) == 0:
        abort(404)
    return jsonify({'user': user})

@app.route('/campinaTags/api/v1.0/updateusers', methods=['POST'])
def update_user():
    if not request.json or not 'id' in request.json or not 'image' in request.json or not 'tags' in request.json:
        abort(400)
    
    current_user_id = request.json['id']
    current_image_id = request.json['image']
    user_to_update = get_users(current_user_id)
    image_to_update = get_images(current_image_id)
    tags_to_update = request.json['tags']

    if len(tags_to_update) == 0:
	abort(400)
    if len(user_to_update) == 0:#New user
	user_to_update = {'id' : current_user_id, 'points' : 0}
	users[current_user_id] = user_to_update
    if len(image_to_update) == 0:#New image
	image_to_update = {'image': current_image_id, 'tags': {}}
	images[current_image_id] = image_to_update

    #Computing points!
    points = 0
    total_occurrences = sum(image_to_update['tags'].values())
    for tag in tags_to_update:
  	if not tag in image_to_update['tags'].keys():#New tag!
		points += 10
		image_to_update['tags'][tag] = 1
	else:#Computing concordance level with other people, more points are given to more common tags!
		points += 5 * (image_to_update['tags'][tag] / total_occurrences)
		image_to_update['tags'][tag] += 1

    #Updating set of tags!      
    image_to_update['tags'].update(tags_to_update)

    #Updating points of user
    user_to_update['points'] += points

    return jsonify({'user': user_to_update}), 201

def get_images(image_id):
    if not images.has_key(image_id):
	return {}
    return images[image_id]

@app.route('/campinaTags/api/v1.0/images', methods=['GET'])
@auth.login_required
def get_all_images():
    return jsonify({'images': images})

@app.route('/campinaTags/api/v1.0/images/<string:image_id>', methods=['GET'])
def get_images_per_id(image_id):
    image = get_images(image_id)
    if len(image) == 0:
        abort(404)
    return jsonify({'image': image})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@auth.get_password
def get_password(username):
    if username == 'admin':
        return hashlib.sha224("CampinaT@gs565").hexdigest()
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

if __name__ == '__main__':
    app.run(debug=True)
