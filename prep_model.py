from flask import Flask, request, jsonify
from flask_restful import Api,Resource,abort,reqparse,marshal_with,fields
from flask_cors import CORS
from flask import Response

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import pickle

import py_eureka_client.eureka_client as eureka_client
import requests

app = Flask(__name__)

#Connect to Eureka Server
eureka_client.init(eureka_server="http://localhost:8761/eureka/",
                        app_name="fraud_api_prep_model",
                        instance_port=1000
)

app.config['JSON_SORT_KEYS'] = False
api=Api(app)

#TODO Delete later
@app.route('/', methods=['GET'])
def index():
    return 'Preparation Model'
#TODO delete later


def Prep_Model(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df2 = df.copy()
    target = list(df2['Staus_Stamp'].unique())
    d = []
    s = []
    for i in target:
        s.append(len(df2[df2.Staus_Stamp == i]))
    oversampled_data = pd.concat([ df2[df2['Staus_Stamp']=='Non_Fraud'].sample(s[s.index(max(s))], replace=True), 
                                    df2[df2['Staus_Stamp']=='Fraud'].sample(s[s.index(max(s))], replace=True),
                                    df2[df2['Staus_Stamp']=='Abuse'].sample(s[s.index(max(s))], replace=True) ])
    df2 = oversampled_data
    df2 = df2.reset_index(drop = True)
    c1 = ['Channel','PlanCode' ,'PolicyNumber','ProductName' ,'Sex','TypeOfClaim','ICDCode']
    c = list(df2.columns.values)

    for i in c :
        x = 0
        for j in range(len(df2)):
            if type(df2[i].iloc[j]) == str :
                x = df2[i].iloc[j]
        if type(x) == str:

            df2[i] = df2[i].astype('str')
    num = ['IssueAge',
        'Attain_Age',
        'AmountOfClaim',
        'SubmitClaimAmount',
        'SumInsured',
        'ModalNetPremium',
        'NumberOfDaysHospitalization',]
    encode = [] #d
    for i in c1:
        df2[i] = df2[i].str.strip()
        onehot = pd.get_dummies(df[i])
        encode.append(onehot)
    d = pd.concat(encode,axis = 1)
    data = pd.concat([df2['InsuredID'],d,df2[num],df2['Staus_Stamp']],axis = 1).reset_index(drop = True)
    data = data.fillna(0)
    x = data.iloc[:,1:len(data.columns.values)-2]
    y = data.iloc[:,len(data.columns.values)-1]
    from sklearn.model_selection import train_test_split
    x_train, x_test, y_train, y_test = train_test_split(x,
                                                        y,
                                                        test_size=0.3, random_state=123)

    clf = DecisionTreeClassifier().fit(x_train,y_train)
    prob = clf.predict_proba(x_test)
    cls = list(clf.classes_)
    print(cls)
    index = list(x_test.index)
    newdf = pd.DataFrame()
    newdf['member'] = data['InsuredID'].iloc[index]
    newdf['member']  = newdf['member'].str.rstrip()
    for i in range(len(cls)):
        l = []
        for j in range(len(prob)):
            l.append(prob[j][i])
        newdf[cls[i]] = l
    
    df = newdf.to_dict('records')
    
    return  df

@app.route('/getnewdf/<string:query>,<string:server>,<string:database>', methods=['GET'])
def prep_model_data(query, server, database):
    #get json from fraud_database
    response = requests.get('http://127.0.0.1:9090/fraud_data/getdata/'+query+','+server+','+database)

    #parse json to dataframe
    df = pd.json_normalize(response.json())

    return jsonify(Prep_Model(df))

if __name__ == "__main__":
    app.run(debug=True, port=1000)