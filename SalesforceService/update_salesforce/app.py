import json
import requests
import os
from userApp import UserApp

def lambda_handler(event, context):
    try:
        # get the data for the salesforce update
        record = json.loads(event['Records'][0]['body'])
        message = record["Message"]
        messageJson = json.loads(message)
        userId = messageJson["userId"]

        url = os.environ['dataUrl'] + str(userId)
        requestHeaders = {'X-SPLASH-SERVICE-USER-ID': os.environ['serviceUser'], 'X-SPLASH-API-TOKEN': os.environ['serviceToken']}
        response = requests.get(url, headers=requestHeaders,  verify=False)
        data = json.loads(response.text)
   
        ua = UserApp(data[0])
        
        items = {"items": [ua.__dict__]}
        
        # get access token
        url = os.environ['tokenUrl']
        tokenResponse = requests.post(url,
            json={
                "grant_type": "client_credentials",
                "client_id": os.environ['clientId'],
                "client_secret": os.environ['clientSecret'],
                "scope": "data_extensions_write data_extensions_read"})
        
        # check status
        if tokenResponse.status_code != 200:
             return {
                "statusCode": tokenResponse.status_code,
                "body": {
                    "message": "unable to get token",
                    "data": tokenResponse.text
                },
            }
        json_tokenResponse = tokenResponse.json()
        token = json_tokenResponse['access_token']


        # update salesforce
        url = os.environ['dataExtUrl']
        headers = ({
          'Authorization'   : 'Bearer ' + token,
          'Content-Type'    : 'application/json'})

        updateResult = requests.put(url, json=items, headers=headers)
  
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)
        raise e

    print("statusCode: " + str(updateResult.status_code) 
        + "; reason: " + updateResult.reason 
        + "; text: " + updateResult.text)
    return {
        "statusCode": updateResult.status_code,
        "body": {
            "message": updateResult.reason,
            "data": updateResult.text
        },
    }
