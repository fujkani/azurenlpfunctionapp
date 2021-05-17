#region Imports
#from shared_code import helper_function
from shared_code import commonHelper

import base64
import azure.functions as func
import os

import json

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from sentry_sdk.integrations.serverless import serverless_function
#endregion Imports

#region Vars

inputSchema = {
    "type": "object",
    "properties": {
        "resume": {"type": "string"},
        "job": {"type": "string"}
    },
    "required": [
        "resume",
        "job"
    ]
}

#endregion Vars

#region Custom Methods

#method to generate match score between resume and job
def match(resumetext, jobtext):
    #try:
    theTwoTexts = [resumetext, jobtext]

    myCV = CountVectorizer()
    countMatrix = myCV.fit_transform(theTwoTexts)
    matchPerc = cosine_similarity(countMatrix)[0][1]*100

    return matchPerc

    #except Exception as e:
    #    return ({'error': str(e)})

#endregion Custom Methods

@serverless_function
def main(req: func.HttpRequest) -> func.HttpResponse:

    try:

        msg = 'Function ' + os.environ["AZURE_FUNCTIONS_ENVIRONMENT"].lower() + 'match initiated'
        commonHelper.capture_message(msg)
        commonHelper.logging.info(msg)

        # Input validation
        try:
            req_body = req.get_json()
        except ValueError:
            res = json.dumps({'error': 'Wrong input. Expecting schema: ' + ''.join(json.dumps(inputSchema))})
            commonHelper.logging.error(res)
            commonHelper.capture_message(res)
            return func.HttpResponse(res, status_code=400)
        else:
            isValid = commonHelper.validateJson(req_body, inputSchema)
            if not isValid:
                res = json.dumps({'error': 'Wrong input. Expecting schema: ' + ''.join(json.dumps(inputSchema))})
                commonHelper.logging.error(res)
                commonHelper.capture_message(res)
                return func.HttpResponse(res, status_code=400)

        resumeBase64 = req_body.get('resume')
        jobBase64 = req_body.get('job')

        if not commonHelper.isBase64(resumeBase64):
            resumeText = resumeBase64
            #res = json.dumps({'error': 'Expecting base64 encoding'})
            #commonHelper.logging.error(res)
            #commonHelper.capture_message(res)
            #return func.HttpResponse(res, status_code=400)

        else:
            resumeText = str(base64.b64decode(resumeBase64), "utf-8")
    

        if not commonHelper.isBase64(jobBase64):
            jobText = jobBase64
        else:
            jobText = str(base64.b64decode(jobBase64), "utf-8")


        ret = match(resumeText, jobText)
        res = json.dumps({'message': {'score': ret }})

        return func.HttpResponse(res, status_code=200)

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return func.HttpResponse(json.dumps({'error1': str(e)}), status_code=500)
        
