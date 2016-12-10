from bson.objectid import ObjectId
from flask import render_template, request, json, Response, redirect, url_for
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

@app.route('/clear_database', methods=['GET'])
def clear_database():
    mongo.db[USERS_DB].drop()
    mongo.db[DONATIONS_DB].drop()

    return Response('Cleaned database!', status=200)

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
    post['is_shopper'] = False

    insert_result = users_db.insert_one(post)
    assert insert_result.acknowledged

    return Response(get_users(), status=200)

@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    params = ['id', 'user_id', 'object']
    id_idx, user_id_idx = params.index('id'), params.index('user_id')
    args = [request.form[param] for param in params]
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

    return Response(get_donations(), status=200)

@app.route('/api/add_sale', methods=['POST'])
def add_route():
    params = ['donation_id', 'amount', 'buyer_id']
    donation_id_idx = params.index('donation_id')
    amount_idx = params.index('amount')
    buyer_id_idx = params.index('buyer_id')
    args = [request.form[param] for param in params]
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

    # Mark it as a shopper.
    users_db.update_one({PRIMARY_KEY : args[buyer_id_idx]},
                        {'$set' : {'is_shopper' : True}})

    # Find out the details of the user that donation refers to.
    user = users_db.find_one({PRIMARY_KEY : donation['user_id']})
    assert user

    # Send him a message.
    sms_body = 'Hi {}! Your {} donation ({}) to British Heart Foundation ' \
               'reached {}\'s home. Thank you.' \
        .format(user['name'], donation['object'], args[amount_idx], \
                buyer['name'])
    send_sms(user['phone'], sms_body)

    return Response(get_sales(), status=200)

@app.route('/api/give_thanks', methods=['POST'])
def give_thanks():
    sms_arg = request.form['sms']
    if not sms_arg:
        return Response('Failure: some arguments are not valid', status=400)

    users_db = mongo.db[USERS_DB]
    counter = 0

    for user in users_db.find():
        if user['is_shopper']:
            send_sms(user['phone'], sms_arg)
            users_db.update_one({PRIMARY_KEY : user[PRIMARY_KEY]},
                                {'$set' : {'is_shopper' : False}})
            counter += 1

    print('Sent sms to {} people'.format(counter))
    return Response(get_give_thanks(), status=200)

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
def get_give_thanks():
    return render_template('give_thanks.html')


@app.route('/new_video', methods=['GET'])
def new_video():
    return render_template('index.html')


@app.route('/new_video', methods=['POST'])
def new_video_post():
    company_name = request.form['company_name']
    value = request.form['value']

    _id = mongo.db.videos.insert({'company_name': company_name, 'value': value})
    return redirect(url_for('get_video', _id=_id))


@app.route('/videos/<_id>', methods=['GET'])
def get_video(_id):
    video = mongo.db.videos.find_one({'_id': ObjectId(_id)})

    captions = json.dumps([{
        'text': 'At {} we care'.format(video['company_name']),
        'time': 60 + 3,
        'duration': 6,
        'x': 50,
        'y': 50,
        'size': 4,
    }, {
        'text': 'We give for a better future',
        'time': 60 + 12,
        'duration': 6,
        'x': 50,
        'y': 50,
        'size': 4,
    }, {
        'text': 'This year, our donations brought {} to research'.format(video['value']),
        'time': 60 + 21,
        'duration': 7,
        'x': 50,
        'y': 50,
        'size': 4,
    }])
    return render_template('video.html', captions=captions)
