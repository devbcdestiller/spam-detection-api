from flask import Flask, request, jsonify
from flask_cors import CORS
from pymemcache.client.base import Client
from packages.preprocessor import token_mail_dict as mail_tokenizer
from packages.preprocessor import token_sms_dict as sms_tokenizer
import packages.preprocessor as preprocessor
import ast
import requests
import json
import base64

VERSION = 'v1'
BATCH_LIMIT = 50

# URI which points to the tensorflow-serving model
RNN_MAIL_URI = 'http://rnn_mail:8501/v1/models/rnnmail_model'
RNN_SMS_URI = 'http://rnn_sms:8503/v1/models/rnnsms_model'

# Configure global variables for memcache
MEMCACHE_CLIENT = Client(('memcache', 11211), no_delay=True)
MEMCACHE_EXPIRE = 60

app = Flask(__name__)
cors = CORS(app, resources={r"/v1/*": {"origins": "*"}})


@app.route(f'/{VERSION}/predict/<string:model>', methods=['POST'])
def predict(model: str):
    accepted_routes = ['sms', 'mail']

    if model not in accepted_routes:
        return jsonify(message=f'Route {model} not in accepted routes: {accepted_routes}'), 404

    if request.is_json:
        input_message = request.json['input_message']
    else:
        input_message = request.form['input_message']

    b64 = base64.urlsafe_b64encode(bytes(input_message, 'utf-8'))
    memcache_key = b64[-32:-1]

    if MEMCACHE_CLIENT.get(memcache_key) is not None:
        cached_result = MEMCACHE_CLIENT.get(memcache_key)
        cached_result = ast.literal_eval(cached_result.decode('utf-8'))
        prediction = cached_result['percent']
        classification = cached_result['classification']
        return jsonify(message='cached prediction', model=f'{model}', input_message=f'{input_message}', spam_percent=f'{prediction*100}', classification=f'{classification}')

    if model == 'mail':
        encoded_message = preprocessor.encode_message([input_message], mail_tokenizer)
        request_url = f'{RNN_MAIL_URI}:predict'
    else:
        encoded_message = preprocessor.encode_message([input_message], sms_tokenizer)
        request_url = f'{RNN_SMS_URI}:predict'

    instances = encoded_message.tolist()
    data = json.dumps({'instances': instances})
    response = requests.post(request_url, data=data)
    result = json.loads(response.text)
    prediction = result['predictions'][0][0]
    classification = 'spam' if prediction > 0.5 else 'ham'
    result = {'percent': prediction,
              'classification': classification}

    MEMCACHE_CLIENT.add(memcache_key, result, expire=MEMCACHE_EXPIRE, noreply=False)

    return jsonify(model=f'{model}', input_message=f'{input_message}', spam_percent=f'{prediction*100}', classification=f'{classification}')


@app.route(f'/{VERSION}/predict/batch/<string:model>', methods=['POST'])
def batch(model: str):
    accepted_routes = ['sms', 'mail']

    if model not in accepted_routes:
        return jsonify(message=f'Route {model} not in accepted routes: {accepted_routes}'), 404

    if not request.is_json:
        return jsonify(message=f'Route batch/{model} accepts only json formatted input.'), 404

    input_messages = request.json['input_messages']
    
    if len(input_messages) > BATCH_LIMIT:
        return jsonify(message=f'Batch limit exceeded. Batch processing only allows a limit of 50 messages.')

    if model == "mail":
        preprocessed = preprocessor.encode_message(input_messages, mail_tokenizer)
        request_url = f'{RNN_MAIL_URI}:predict'
    else:
        preprocessed = preprocessor.encode_message(input_messages, sms_tokenizer)
        request_url = f'{RNN_SMS_URI}:predict'

    data = json.dumps({'instances': preprocessed.tolist()})
    response = requests.post(request_url, data=data)
    result = json.loads(response.text)
    predictions = []

    for message, prediction in tuple(zip(input_messages, result['predictions'])):
        predictions.append({
            'message': message,
            'spam_percent': prediction[0] * 100,
            'classification': 'spam' if prediction[0] > 0.5 else 'ham'
        })

    return jsonify(length=len(input_messages), model=model, predictions=predictions)


@app.route(f'/{VERSION}/status/<string:model>', methods=['GET'])
def status(model: str):
    accepted_routes = ['sms', 'mail']

    if model not in accepted_routes:
        return jsonify(message=f'Route {model} not in accepted routes: {accepted_routes}'), 404

    if model == 'mail':
        response = requests.get(RNN_MAIL_URI)
    else:
        response = requests.get(RNN_SMS_URI)

    result = json.loads(response.text)

    return jsonify(message=result)


@app.route('/')
def index():
    return 'Visit https://github.com/devbcdestiller/spam-detection-api to read the docs'


# Comment out code below in production
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
