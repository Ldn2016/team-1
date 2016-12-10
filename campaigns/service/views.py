from flask import render_template, request, Response
from service import app, mongo
from service.sms_api import send_sms

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
    args = [request.form[param] for param in params]
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
    params = ['id', 'user_id', 'object']
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

def make_message(donor, buyer, donation):
    sms_body = 'Hi {}! Your {} donation ({}) to British Heart Foundation ' \
               'reached {}\'s home. Thank you.' \
        .format(donor['name'], donation['amount'], donation['object'],
                buyer['name'])

    return sms_body

@app.route('/api/add_sale', methods=['POST'])
def add_route():
    params = ['donation_id', 'amount', 'buyer_id']
    donation_id_idx = params.index('donation_id')
    buyer_id_idx = params.index('buyer_id')
    args = [request.form.get(param) for param in params]
    if not all(args):
        return Response('Failure: some arguments are not valid', status=400)

    users_db = mongo.db[USERS_DB]
    donations_db = mongo.db[DONATIONS_DB]

    # Check that the referenced donation exists.
    donation = donations_db.find_one({PRIMARY_KEY : args[donation_id_idx]})
    if not donation:
        return Response('Failure: referenced donation id does not exist',
                        status=400)

    # Check that the buyer exists.
    buyer = users_db.find_one({PRIMARY_KEY : args[buyer_id_idx]})
    if not buyer:
        return Response('Failure: referenced buyer id does not exist',
                        status=400)

    # Find out the details of the user that donation refers to.
    user = users_db.find_one({PRIMARY_KEY : donation['user_id']})
    assert user

    # Send him a message.
    send_sms(user['phone'], make_message(user, buyer, donation))

    return Response(
        'Success: sent a thank you message to user {}'.format(user),
        status=200)

@app.route('/users', methods=['GET'])
def get_users():
    users_db = mongo.db[USERS_DB]
    users = users_db.find()

    return render_template('users.html', users=users)

@app.route('/donations', methods=['GET'])
def get_donations():
    donations_db = mongo.db[DONATIONS_DB]
    donations = donations_db.find()

    return render_template('donations.html', donations=donations)

@app.route('/sales', methods=['GET'])
def get_sales():
    return render_template('sales.html')
    
@app.route('/give_thanks', methods=['GET'])
def give_thanks():
    return render_template('give_thanks.html')
