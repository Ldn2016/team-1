from flask import request, Response
from service import app, mongo

@app.route('/', methods=['GET'])
def index():
    # Sanity checks.
    posts = mongo.db.posts
    post_id = posts.insert_one({'author' : 'Author'})
    assert posts.find_one({'author' : 'Author'})

    # Remove everything.
    posts.remove({})

    return Response('Sanity checks successful!', status=200)

USERS_DB = 'users'
DONATIONS_DB = 'donations'
PRIMARY_KEY = '_id'

@app.route('/api/add_user', methods=['POST'])
def add_user():
    params = ['id', 'name', 'phone', 'email']
    id_idx = params.index('id')
    args = [request.form.get(param) for param in params]
    if not all(args):
        return Response('Failure: some arguments are not valid', status=400)

    users_db = mongo.db[USERS_DB]

    # Make sure it is not a duplicate.
    if users_db.find_one({PRIMARY_KEY : args[id_idx]}):
        return Response('Failure: duplicate user', status=400)

    # Rename the 'id' key to how MongoDB expects it.
    params[id_idx] = PRIMARY_KEY

    # Add it to the users database.
    post = {param : arg for param, arg in zip(params, args)}
    insert_result = users_db.insert_one(post)
    assert insert_result.acknowledged

    return Response(
        'Success: Added a new user with id {}!'.format(args[id_idx]),
        status=200)

@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    # TODO: Add more relevant params.
    params = ['id', 'user_id']
    id_idx, user_id_idx = params.index('id'), params.index('user_id')
    args = [request.form.get(param) for param in params]
    if not all(args):
        return Response('Failure: some arguments are not valid', status=400)

    # Check that the referenced user exists.
    users_db = mongo.db[USERS_DB]
    if not users_db.find_one({PRIMARY_KEY : args[user_id_idx]}):
        return Response('Failure: referenced user does not exist', status=400)

    # Check that the referenced donation is not a duplicate.
    donations_db = mongo.db[DONATIONS_DB]
    if donations_db.find_one({PRIMARY_KEY : args[id_idx]}):
        return Response('Failure: duplicate donation', status=400)

    # Rename the 'id' key to how MongoDB expects it.
    params[id_idx] = PRIMARY_KEY

    # Add it to the donations database.
    post = {param : arg for param, arg in zip(params, args)}
    insert_result = donations_db.insert_one(post)
    assert insert_result.acknowledged

    return Response('Success: Added a new donation with id {}, from user{}'\
                        .format(args[id_idx], args[user_id_idx]), status=200)

@app.route('/api/add_sale', methods=['POST'])
def add_route():
    # TODO:
    return Response('Success:', status=200)
