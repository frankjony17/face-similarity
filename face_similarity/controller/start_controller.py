from flask import Blueprint

start_route = Blueprint('start_route', __name__)


@start_route.route('/')
def welcome():
    return 'Welcome to Face Similarity API, read documentation in /docs for further questions.', 200
