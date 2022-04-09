from flask import Flask, request, jsonify
from flask_cors import CORS
from packages.preprocessor import token_mail_dict as mail_tokenizer
from packages.preprocessor import token_sms_dict as sms_tokenizer
import packages.preprocessor as preprocessor
import requests
import json


VERSION = 'v1'

# URI which points to the tensorflow-serving model
RNN_MAIL_URI = 'http://rnn_mail:8501/v1/models/rnnmail_model'
RNN_SMS_URI = 'http://rnn_sms:8503/v1/models/rnnsms_model'

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

    return jsonify(model=f'{model}', message=f'{input_message}', spam_precent=f'{prediction*100}', classification=f'{classification}')


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
