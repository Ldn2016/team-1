from bson.objectid import ObjectId
from flask import Flask, render_template, request, json, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_video', methods=['POST'])
def new_video():
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


if __name__ == '__main__':
    app.run()
