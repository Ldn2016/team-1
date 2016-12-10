from flask import Flask, render_template, request, json
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_video', methods=['POST'])
def new_video():
    return request.form['company_name']


@app.route('/videos/<url>', methods=['GET'])
def get_video(url):
    captions = json.dumps([{
        'text': 'J.P. Morgan',
        'time': 1.2,
        'duration': 4,
        'x': 50,
        'y': 40,
        'size': 7,
    }, {
        'text': 'Hugo Boss',
        'time': 1.2,
        'duration': 4,
        'x': 50,
        'y': 70,
        'size': 7,
    }])
    return render_template('video.html', captions=captions)


if __name__ == '__main__':
    app.run()
