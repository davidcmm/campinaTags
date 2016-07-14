#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth

from sets import Set

import json

auth = HTTPBasicAuth()
app = Flask(__name__)

users = [
    {
        'id': 1,
        'points': 0
    },
    {
        'id': 2,
        'points': 10
    }
]

images = [
    {
        'image': "joao_pessoa",
        'tags': Set(["verde", "amplo"])
    },
    {
        'image': "odon_bezzerra",
        'tags': Set(["sujo", "velho"])
    }
]

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/campinaTags/api/v1.0/users', methods=['GET'])
def get_all_users():
    return jsonify({'users': users})

def get_users(user_id):
    user = [user for user in users if user['id'] == user_id]
    return user

@app.route('/campinaTags/api/v1.0/users/<int:user_id>', methods=['GET'])
def get_users_per_id(user_id):
    user = get_users(user_id)
    if len(user) == 0:
        abort(404)
    return jsonify({'user': user[0]})

@app.route('/campinaTags/api/v1.0/updateusers', methods=['POST'])
def update_user():
    if not request.json or not 'id' in request.json or not 'image' in request.json or not 'tags' in request.json:
        abort(400)
    
    user_to_update = get_users(request.json['id'])[0]
    image_to_update = get_images(request.json['image'])[0]
   
    tags_to_update = request.json['tags']
    if len(user_to_update) == 0 or len(image_to_update) == 0 or len(tags_to_update) == 0:
	abort(400)

    #Computing points!
    points = 0
    for tag in tags_to_update:
  	if not tag in image_to_update['tags']:
		points += 10
	else:
		points += 5

    #Updating set of tags!      
    image_to_update['tags'].update(tags_to_update)

    #Updating points of user
    user_to_update['points'] += points

    return jsonify({'user': user_to_update}), 201

@app.route('/campinaTags/api/v1.0/images', methods=['GET'])
@auth.login_required
def get_all_images():
    new_images = []
    for image in images:
	new_images.append({'image': image['image'], 'tags': list(image['tags'])})

    return jsonify({'images': new_images})

def get_images(image_id):
    image = [image for image in images if image['image'] == image_id]
    return image

@app.route('/campinaTags/api/v1.0/images/<string:image_id>', methods=['GET'])
def get_images_per_id(image_id):
    image = get_images(image_id)
    if len(image) == 0:
        abort(404)
    new_images = []
    for im in image:
	new_images.append({'image': im['image'], 'tags': list(im['tags'])})
    return jsonify({'image': new_images[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

if __name__ == '__main__':
    app.run(debug=True)
