from flask import request, Response
from service import app, mongo
from service.models import *

@app.route('/', methods=['GET'])
def index():
    # Sanity checks.
    posts = mongo.db.posts
    post_id = posts.insert_one({'author' : 'Calin'})
    assert posts.find_one({'author' : 'Calin'})

    # Remove everything.
    posts.remove({})

    return Response('Sanity checks successful!', status=200)

@app.route('/api/add_user', methods=['POST'])
def add_user():
    params = ['id', 'name', 'phone', 'email']
    args = [request.form.get(param) for param in params]
    if not all(args):
        return Response('Failure: some arguments are not valid', status=400)

    posts = mongo.db.posts

    # Rename the 'id' key to how MongoDB expects it.
    params[0] = '_id'

    # Make sure it is not a duplicate.
    if posts.find_one({params[0] : args[0]}):
        return Response('Failed: duplicate user', status=400)

    # Add it to the database.
    post = {param : arg for param, arg in zip(params, args)}
    insert_result = posts.insert_one(post)
    assert insert_result.acknowledged

    return Response('Success: Added a new user with id {}!'.format(post['_id']),
                    status=200)

@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    # TODO:
    return Response('Success:', status=200)

@app.route('/api/add_sale', methods=['POST'])
def add_route():
    # TODO:
    return Response('Success:', status=200)
