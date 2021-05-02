from flask import Flask, request, jsonify
import os
import dialogflow
import requests
import json
from google.api_core.exceptions import InvalidArgument
from google.protobuf.json_format import MessageToDict
import pandas as pd

app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to Tax Assistant!"

@app.route("/responder", methods=['GET', 'POST'])
def responder():

    if request.method == 'GET':        
        request_text = request.args.get('text', default="", type=str)
        response_text = "Hi there!" + request_text
        return jsonify(reply = response_text)

    if request.method == 'POST':
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
        DIALOGFLOW_PROJECT_ID = '<Data>'
        DIALOGFLOW_LANGUAGE_CODE = 'en'
        SESSION_ID = 'unique'

        request_text = request.json['text_query']
        response = detect_intent_texts(DIALOGFLOW_PROJECT_ID, SESSION_ID, request_text, DIALOGFLOW_LANGUAGE_CODE)    

        # Checking Fullfillment For Graphs

        try:
            moveforward = response.query_result.all_required_params_present
        except:
            moveforward = False

        if moveforward == False:
            response_json = Get_Formatted_Output(response.query_result.fulfillment_text, False)
            return response_json

        # If Request id Not FullFilled
        test = response.query_result.parameters
        output = MessageToDict(test)  

        # Creating DataFrame Using CSV
        datatable = pd.read_csv('AssistantDB.csv')

        a =  {
                'question1': None,
                'ToFind': None,
                'CompanyName': None,
                'CompanyLocation' : None,
                'AuthorityName' : None,
                'intent': "Count",
                'ReturnID':None,
                'last':None,
                'EventName':None,
                'AY':None, 
                'Ground':None,
                'GroundStatus':None,
                'duplicate_entries': None,
                'plot_type':None,
                'ContingentLiability':None,
                'WinProbability':None

                }


        text_to_speech_aider=  {
                'CompanyName': "Companies",
                'CompanyLocation': "locations",
                'AuthorityName' : "Authorities",
                'ReturnID':'Return ID',
                'EventName':"events",
                'AY':"assessment years",
                'Ground':"grounds",
                'records':"records",
                'ContingentLiability':"contingent liabilities",
                'WinProbability':"probability of winning"
                }

        a['intent']=response.query_result.intent.display_name

        try:
                a['ToFind']=output['ToFind']
                if  a['ToFind'] == []:
                    a['ToFind'] = ['CompanyName']
        except:
                pass
        try:
                a['CompanyName']=output['CompanyName']
                if  a['CompanyName'] == []:
                    a['CompanyName'] = None
        except:
                pass
        try:
                a['CompanyLocation']=output['CompanyLocation']
                if  a['CompanyLocation'] == []:
                    a['CompanyLocation'] = None
        except:
                pass
        try:
                a['AuthorityName']=output['AuthorityName']
                if  a['AuthorityName'] == []:
                    a['AuthorityName'] = None
        except:
                pass
        try:
                a['ReturnID']=output['ReturnID']
                if  a['ReturnID'] == []:
                    a['ReturnID'] = None
        except:
                pass
        try:
                a['EventName']=output['EventName']
                if  a['EventName'] == []:
                    a['EventName'] = None
        except:
                pass
        try:
                a['AY']= output['AY']
                if  a['AY'] == []:
                    a['AY'] = None
        except:
                pass
        try:
                a['Ground']=output['Ground']
                if  a['Ground'] == []:
                    a['Ground'] = None
        except:
                pass
        try:
                a['GroundStatus']=output['GroundStatus']
                if  a['GroundStatus'] == []:
                    a['GroundStatus'] = None
        except:
                pass
        try:
                a['duplicate_entries']=output['duplicate_entries']
                if  a['duplicate_entries'] == "":
                    a['duplicate_entries'] = None
        except:
                pass
        try:
                a['plot_type']=output['plot_type']
                if  a['plot_type'] == []:
                    a['plot_type'] = None
        except:
                pass

        try:
                a['WinProbability']=output['WinProbability']
                if  a['WinProbability'] == []:
                    a['WinProbability'] = None
        except:
                pass

         
        
        # Intents added here
        if a['intent'] == "Count":
                datatable = sorter_main(datatable,a)
                
                if a['ToFind'] == [""]:
                     a['ToFind']=["CompanyName"]
                     temp =  a['ToFind'][0]

                else:
                     temp = a['ToFind'][0]

                datatable = datatable[[temp]]
                
                if a['duplicate_entries'] is None:
                    datatable= datatable.drop_duplicates()
              
                x = datatable[temp].count()

                if a['duplicate_entries'] is not None:
                    temp='records'

                #return Json area
                reply = "I scanned through the data and I found the total number of {} to be {}.".format(text_to_speech_aider[temp],x)
                return Get_Formatted_Output(reply,False)

        if a['intent'] == "test_fulfilment":                
                return Get_Formatted_Output(response.query_result.fulfillment_text,False)

        ##small talk ones:
        if  a['intent'] == "Default Welcome Intent":                
                return Get_Formatted_Output(response.query_result.fulfillment_text,False)


        if a['intent'] == '' :
                return Get_Formatted_Output(response.query_result.fulfillment_text,False)


        if a['intent'] == "PlotGraph":
                datatable = sorter_main(datatable,a)
                ##plot begin               

                y_var = a['ToFind'][0]
                if len(a['ToFind']) > 1:
                    x_var = a['ToFind'][1]
                else:
                    x_var = a['ToFind'][0]
                
                if len(a['ToFind']) > 1:
                    horizontal_stack = pd.concat([datatable[[x_var]], datatable[[y_var]]], axis=1)
                    horizontal_stack= horizontal_stack.groupby([x_var])[y_var].count()
                else:
                    horizontal_stack = datatable.groupby([x_var])[x_var].count()

                response = "I have plotted number of records of {} with respect to the {} as per your search.".format(text_to_speech_aider[y_var],text_to_speech_aider[x_var])
                graph_data = horizontal_stack.to_json(orient='split')#[1:-1].replace('},{', '} {')
                graph_data_f = json.loads(graph_data)
                json_packet = {'response': response,
                               'graph': True,
                               'graph_type': a['plot_type'][0],
                               'graph_x':text_to_speech_aider[x_var],
                               'graph_y':text_to_speech_aider[y_var],
                               'graph_data': graph_data_f,
                               'note':"index is x axis, data is value"
                               }
                return jsonify(json_packet)

        if a['intent'] == "FindValue":
                datatable = sorter_main(datatable,a)               
                temp = a['ToFind'][0]
                datatable = datatable[temp]
                datatable= datatable.drop_duplicates()
                i = datatable.count()
                str_val=""
                p=0
                while p < i :
                    str_val = str_val + str(datatable.tolist()[p])
                    p= p+1
                    if p<i :
                        str_val = str_val + ", "

                #return Json area 
                if temp == 'WinProbability':
                        reply = "The {} for tax services in 2017 is: {}".format(text_to_speech_aider[temp],"High Chances of Winning.")  
                else:
                        reply = "I found following {} to be matching your search requirements: {}".format(text_to_speech_aider[temp],str_val)
                if i == 0:
                    reply = "I couldn't find any {} to be matching your search requirements.".format(text_to_speech_aider[temp])
                return Get_Formatted_Output(reply, False)  
            
        return Get_Formatted_Output(response.query_result.fulfillment_text, False)
                     


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)

        # Basic Query and Result 
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input)
        except InvalidArgument:
            raise   

        return response

# Format the Response
def Get_Formatted_Output(fulfillment_text, isGraph):
    response_json = {'response':fulfillment_text, 'graph': isGraph}
    response_json = jsonify(response_json)
    response_json.headers.add('Access-Control-Allow-Origin', '*')
    return response_json


# DataFrame Sorters
def sorter_location(x,a):
        x = x[x['CompanyLocation'].isin(a['CompanyLocation'])]
        return x

def sorter_companyName(x,a):
        x = x[x['CompanyName'].isin(a['CompanyName'])]
        return x

def sorter_eventName(x,a):
        x = x[x['EventName'].isin(a['EventName'])]
        return x

def sorter_authorityName(x,a):
        x = x[x['AuthorityName'].isin(a['AuthorityName'])]
        return x

def sorter_assessmentYear(x,a):
        x = x[x['AY'].isin(a['AY'])]
        return x

def sorter_ground(x,a):
        x = x[x['Ground'].isin(a['Ground'])]
        return x

def sorter_groundStatus(x,a):
        x = x[x['GroundStatus'].isin(a['GroundStatus'])]
        return x

def sorter_WinProbability(x,a):
        x = x[x['WinProbability'].isin(a['WinProbability'])]
        return x

    ## Fall through filter
def sorter_main(x,a):
        if a['CompanyName'] is not None:
            x = sorter_companyName(x,a)

        if a['CompanyLocation'] is not None:
            x = sorter_location(x,a)

        if a['EventName'] is not None:
            x = sorter_eventName(x,a)

        if a['AuthorityName'] is not None:
            x = sorter_authorityName(x,a)

        if a['AY'] is not None:
            x = sorter_assessmentYear(x,a)

        if a['Ground'] is not None:
            x = sorter_ground(x,a)

        if a['GroundStatus'] is not None:
            x = sorter_groundStatus(x,a)

        if a['WinProbability'] is not None:
            x = sorter_WinProbability(x,a)
        return x
