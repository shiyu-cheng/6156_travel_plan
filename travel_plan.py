from flask import Flask 
application = Flask(__name__)

@application.route('/')
def main_page():
    return "This is the main page for travel plan."