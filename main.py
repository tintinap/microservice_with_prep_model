from flask import Flask, request, jsonify
from flask_restful import Api,Resource,abort,reqparse,marshal_with,fields
from flask_cors import CORS
from flask import Response

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import pickle
import pyodbc
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

import py_eureka_client.eureka_client as eureka_client
import requests


app = Flask(__name__)


#Connect to Eureka Server
eureka_client.init(eureka_server="http://localhost:8761/eureka/",
                        app_name="main_fraud_api",
                        instance_port=5000
)

app.config['JSON_SORT_KEYS'] = False
api=Api(app)
auth = HTTPBasicAuth()

#TODO Delete later
@app.route('/', methods=['GET'])
def index():
    return 'Main'
#TODO delete later

def Test_Auth():
    Auth = pd.DataFrame()
    Auth['username'] = ['Test']
    Auth['password'] = ['123']
    user = {}	
    for i in range(len(Auth)):
        user.update({Auth['username'].iloc[i]: generate_password_hash(Auth['password'].iloc[i])})
    return user

@auth.verify_password
def verify_password(username, password):
    users = Test_Auth()
    if username in users and \
            check_password_hash(users.get(username), password):
            return username


@app.route('/Fraud_model/api', methods=['GET'])
@auth.login_required
def get_api():
    query = 'SELECT * FROM Fraud_Dataset'
    server = 'localhost'
    database = 'DataScience'
    #call the prep_model api
    response = requests.get('http://127.0.0.1:9090/prep_model/getnewdf/'+query+','+server+','+database)
    return Response(response, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True, port=5000)