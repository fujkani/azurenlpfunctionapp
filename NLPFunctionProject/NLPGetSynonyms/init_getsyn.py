#region Imports
from shared_code import commonHelper

import os
import azure.functions as func
import json
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

@serverless_function
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

        msg = 'Function ' + os.environ["AZURE_FUNCTIONS_ENVIRONMENT"].lower() + 'getsyn initiated'
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

        if not(commonHelper.isBase64(resumeBase64) and commonHelper.isBase64(jobBase64)):
            res = json.dumps({'error': 'Expecting base64 encoding'})
            commonHelper.logging.error(res)
            commonHelper.capture_message(res)
            return func.HttpResponse(res, status_code=400)

        else:
            res = json.dumps({'message': {'results':[{'term':'build','synonyms':['construct','develop']},{'term':'manage','synonyms':['lead','direct','instruct']}]}})
            return func.HttpResponse(res, status_code=200)

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return func.HttpResponse(json.dumps({'error1': str(e)}), status_code=500)





