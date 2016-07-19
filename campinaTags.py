#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
#from flask.ext.httpauth import HTTPBasicAuth

import hashlib
import json

#Database connection
import psycopg2
import psycopg2.extras
import sys
import pprint

#Decorator!
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

import logging

#Logging configuration!
def configLogging():
    logger = logging.getLogger('campinaTags')
    hdlr = logging.FileHandler('/var/www/campinaTags/campinaTags/campinaTags.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    return logger

#Init Flask and logging!
app = Flask(__name__)
logger = configLogging()

#Data dictionaries
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

images = {
    "joao_pessoa" : {
        'name': "joao_pessoa",
        'tags': {"verde" : 1, "amplo": 1}
    },
    "odon_bezerra" : {
        'name': "odon_bezzerra",
        'tags': {"velho" : 1, "sujo": 1}
    }
}

#Security check decorators: http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

#Index page demonstration!
@app.route('/')
def index():
    return "Hello, World!"

#Retrieving users dic data!
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

#Retrieving images dic data!
def get_images(image_id):
    if not images.has_key(image_id):
	return {}
    return images[image_id]

@app.route('/campinaTags/api/v1.0/images', methods=['GET'])
def get_all_images():
    return jsonify({'images': images})

@app.route('/campinaTags/api/v1.0/images/<string:image_id>', methods=['GET'])
def get_images_per_id(image_id):
    image = get_images(image_id)
    if len(image) == 0:
        abort(404)
    return jsonify({'image': image})

#Generic error response
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Convert string from database to a dictionary!
def stringToDic(dic_string):
    data = dic_string.split(";")
    dic = {}
    for value in data:
	currentData = value.split("=");
	dic[currentData[0]] = int(currentData[1])
    return dic

#Init from DB! Based on https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
def startFromDB():
    global images
    global users
    #Define our connection string
    conn_string = "host='localhost' dbname='campinatags' user='campinatags' password='c@mpin@2016lsD'"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    logger.info("Connected to database ->%s" % ("host='localhost' dbname='campinatags'"))

    # tell postgres to use more work memory
    work_mem = 2048
    cursor.execute('SET work_mem TO %s', (work_mem,))
    #cursor.execute('SHOW work_mem')
    #memory = cursor.fetchone()

    # Retrieve all images!
    try:
	    cursor.execute("SELECT * FROM images")
	    records = cursor.fetchall()
	    if len(records) == 0:
		images = {}
	    else:
		for record in records:
			images[record['name']] = {'name': record['name'], 'tags' : stringToDic(record['tags'])}

	    # Retrieve all users
	    cursor.execute("SELECT * FROM \"user\"")
	    records = cursor.fetchall()
	    if len(records) == 0:
		users = {}
	    else:
		for record in records:
			users[record['id']] = {'id': record['id'], 'points' : record['points']}
	 
	    cursor.close()
	    conn.close()
    except:
            logger.error("Error in selecting from database! %s" % (sys.exc_info()[0]))

#Convert dictionary entry to a string to be stored in database!
def dicToString(dic):
    return ";".join(["%s=%s" % (k, v) for k, v in dic.items()])

#Update database!
def updateDB(image_to_update, user_to_update, new_user, new_image):
    #Define our connection string
    conn_string = "host='localhost' dbname='campinatags' user='campinatags' password='c@mpin@2016lsD'"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    
    try:
	    # Update image!
	    if new_image:
		cur.execute( "INSERT INTO images (name, tags) VALUES (%s, %s)", (image_to_update['name'], dicToString(image_to_update['tags'])) )
	    else:
		cur.execute( "UPDATE images SET tags = (%s) WHERE name = (%s)", (dicToString(image_to_update['tags']), mage_to_update['name']) )

	    # Update user!
	    if new_user:
	    	cur.execute( "INSERT INTO \"user\" (id, points) VALUES (%s, %s)", (user_to_update['id'], user_to_update['points']) )
	    else:
		cur.execute( "UPDATE \"user\" SET points = (%s) WHERE id = (%s)", (user_to_update['points'], user_to_update['id']) )

	    conn.commit()
	    cur.close()
    except:
            logger.error("Error in updating database! %s" % (sys.exc_info()[0]))

#Avoid prohibited strings as inputs!
def checkContent(current_user_id, current_image_id, tags_to_update):
    prohibited_words = ["delete ", "remove ", "insert ", "update ", "alter ", "table"]
    
    if len(current_user_id) == 0 or len(current_image_id) == 0 or len(tags_to_update) == 0:
	return False

    for word in prohibited_words:
	if current_user_id.find(word) or current_image_id.find(word):
		return False
	for tag in tags_to_update:
		if tag.find(word):
			return False

    return True

@app.route('/campinaTags/api/v1.0/updateusers', methods=['POST'])
@crossdomain(origin='https://contribua.org/pybossa/project/CampinaTags/*')
def update_user():
    if not request.json or not 'id' in request.json or not 'image' in request.json or not 'tags' in request.json:
        abort(400)
    
    current_user_id = request.json['id']
    current_image_id = request.json['image']
    user_to_update = get_users(current_user_id)
    image_to_update = get_images(current_image_id)
    tags_to_update = request.json['tags']
    new_user = False
    new_image = False

    if len(tags_to_update) == 0:
	abort(400)
    if len(user_to_update) == 0:#New user
	user_to_update = {'id' : current_user_id, 'points' : 0}
	users[current_user_id] = user_to_update
	new_user = True
    if len(image_to_update) == 0:#New image
	image_to_update = {'name': current_image_id, 'tags': {}}
	images[current_image_id] = image_to_update
	new_image = True

    if not checkContent(current_user_id, current_image_id, tags_to_update):
	return jsonify({''}), 400

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

    updateDB(image_to_update, user_to_update, new_user, new_image)

    return jsonify({'user': user_to_update}), 201

#@auth.get_password
#def get_password(username):
 #   if username == 'admin':
  #      return hashlib.sha224("CampinaT@gs565").hexdigest()
   # return None

#@auth.error_handler
#def unauthorized():
 #   return make_response(jsonify({'error': 'Unauthorized access'}), 403)

#if __name__ == '__main__':
#    app.run(debug=True)
startFromDB()
