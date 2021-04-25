from flask import Flask, request, jsonify
from flask_restful import Api,Resource,abort,reqparse,marshal_with,fields
from flask_cors import CORS
from flask import Response

import pandas as pd
import pyodbc

import py_eureka_client.eureka_client as eureka_client


#TODO delete later
import mysql.connector
#TODO delete later

app = Flask(__name__)

#Connect to Eureka Server
eureka_client.init(eureka_server="http://localhost:8761/eureka/",
                        app_name="fraud_api_database",
                        instance_port=3000
)


app.config['JSON_SORT_KEYS'] = False
api=Api(app)


#TODO Delete later
@app.route('/', methods=['GET'])
def index():
    return 'Data Caller'
#TODO delete later

@app.route('/getdata/<string:query>,<string:server>,<string:database>', methods=['GET'])
def Query_DB(query,server,database):
    #TODO use this for original code
    # cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
    #TODO use this for original code
    #TODO delete later
    cnxn = mysql.connector.connect(host=server, user="admin", password="admin",database=database, auth_plugin='mysql_native_password')
    #TODO delete later
    df = pd.read_sql(query,cnxn)

    return Response(df.to_json(orient="records"), mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True, port=3000)