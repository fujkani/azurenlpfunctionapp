#region Imports
from shared_code import commonHelper

import base64

import azure.functions as func
import os
import re
from typing import Optional
import numpy

import json
from pydantic import BaseModel
import nltk

from sentry_sdk.integrations.serverless import serverless_function

#endregion Imports

#region Vars
inputSchema = {
    "type": "object",
    "properties": {
        "job": {"type": "string"}
    },
    "required": [
        "job"
    ]
}
#endregion Vars



#region Custom Methods

#method to extract person names from text using nltk tokenizer and person label
def extract_names(input_text):
    try:
        person_names = []

        for sent in nltk.sent_tokenize(input_text):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                    person_names.append(
                        ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                    )

        return person_names

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return person_names
        pass

#method to extract phone NOs using regex
def extract_phone_number(input_text):
    try:
        PHONE_REG = re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?", re.S)
        phones = re.findall(PHONE_REG, input_text)
        retPhones = []
        if phones:
            for num in phones:
                phoneNo = ''.join(num)
                if input_text.find(phoneNo) >= 0 and len(phoneNo) < 16:
                    retPhones.append(phoneNo)
        
        return retPhones

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return retPhones
        pass

#method to extract emails NOs using regex
def extract_emails(input_text):
    EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
    return re.findall(EMAIL_REG, input_text)

#method to find skills offline
def extract_skills_offline(input_text):
    try:
    
        #return ''.join(os.listdir(path='/nlp'))

        SKILLS_DB = ['architect','visual studio','sql server','Oracle','gis','machine learning','data science','python','word','excel','English','risk manage', 'Knowledge Management', 'Reporting', 'Risk management', 'IT Governance']
        found_skills = set()

        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.tokenize.word_tokenize(input_text)

        # remove the stop words
        filtered_tokens = [w for w in word_tokens if w not in stop_words]

        # remove the punctuation
        filtered_tokens = [w for w in word_tokens if w.isalpha()]

        # generate bigrams and trigrams (such as artificial intelligence)
        bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
        
        # we search for each token in our skills database
        for token in filtered_tokens:
            if token.lower() in SKILLS_DB:
                found_skills.add(token)

        # we search for each bigram and trigram in our skills database
        for ngram in bigrams_trigrams:
            if ngram.lower() in SKILLS_DB:
                found_skills.add(ngram)

        return found_skills

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return found_skills
        pass


#endregion Custom Methods

# main entry point
@serverless_function
def main(req: func.HttpRequest) -> func.HttpResponse:

    try:

        msg = 'Function ' + os.environ["AZURE_FUNCTIONS_ENVIRONMENT"].lower() + 'match initiated'
        commonHelper.capture_message(msg)
        commonHelper.logging.info(msg)

        if os.environ["AZURE_FUNCTIONS_ENVIRONMENT"] != "Development":
            #Assumes that nltk data is already downloaded into the azure storage share accessible by the app as defined in NLTK_PATH    
            nltk.data.path.clear()
            nltk.data.path.append(os.environ["NLTK_PATH"])

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

        jobBase64 = req_body.get('job')

        if not commonHelper.isBase64(jobBase64):
            #Assuming it's text then
            jobText = jobBase64
            #res = json.dumps({'error': 'Expecting base64 encoding'})
            #commonHelper.logging.error(res)
            #commonHelper.capture_message(res)
            #return func.HttpResponse(res, status_code=400)

        else:
            jobText = str(base64.b64decode(jobBase64), "utf-8")

        phone_numbers = extract_phone_number(jobText)
        emails = extract_emails(jobText)
        skills = extract_skills_offline(jobText)
        names = extract_names(jobText)

        topics = ['architecture','team lead','supervise']
        categories = ['Senior','Manager']

        contacts = {'names': names, 'phones': phone_numbers, 'emails': emails}

        res = json.dumps({'message': {'contacts': contacts, 'topics': topics, 'categories': categories, 'skills': " ".join(skills)}})

        return func.HttpResponse(res, status_code=200)

    except Exception as e:
        commonHelper.logging.error(str(e))
        commonHelper.capture_exception(str(e))
        return func.HttpResponse(json.dumps({'error1': str(e)}), status_code=500)