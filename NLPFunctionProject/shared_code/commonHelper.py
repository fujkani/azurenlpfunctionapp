import os
import base64
import jsonschema
from jsonschema import validate

import azure.functions as func
from sentry_sdk import init, capture_message, capture_exception
import logging
# Note that env var AZURE_FUNCTIONS_ENVIRONMENT is automatically set to Development by Azure Func in your local machine
# This variable needs to be set in Azure Function app configuration. I have already set this.
# Refer to AsBuiltDev.md for more info..

#Every other env variable needs to be set in local.settings.json and also in Azure Function app configuration!!

init(
    os.environ["SENTRY_DSN"],
    environment=os.environ["AZURE_FUNCTIONS_ENVIRONMENT"].lower(),

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)

# Validates a json based on a schema
def validateJson(jsonData, myschema):
    try:
        validate(instance=jsonData, schema=myschema)
    except jsonschema.exceptions.ValidationError as err:
        #print(str(err))
        return False
    return True

# Validates that input is in fact base64 encoded
def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            return False
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False