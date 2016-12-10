from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)

from service import views

if __name__ == "__main__":
    app.run(debug=True)
