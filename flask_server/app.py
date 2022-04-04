from flask import Flask, request, jsonify
import numpy as np
import requests
import base64
import json


# URI which points to the tensorflow-serving model
RNN_MAIL_URI = 'http://rnn_mail:8501/v1/models/rnnmail_model'
RNN_SMS_URI = 'http://rnn_sms:8503/v1/models/rnnsms_model'

app = Flask(__name__)


@app.route('/predict/<string:model>', methods=['POST'])
def predict(model: str):
    accepted_routes = ['sms', 'mail']

    if model not in accepted_routes:
        return jsonify(message=f'Route "{model}" not in accepted routes: {accepted_routes}'), 404

    if model == 'mail':
        response = requests.get(RNN_MAIL_URI)
    else:
        response = requests.get(RNN_SMS_URI)

    result = json.loads(response.text)

    return jsonify(message=result)


@app.route('/status/<string:model>', methods=['GET'])
def status(model: str):
    accepted_routes = ['sms', 'mail']

    if model not in accepted_routes:
        return jsonify(message=f'Route "{model}" not in accepted routes: {accepted_routes}'), 404

    if model == 'mail':
        response = requests.get(RNN_MAIL_URI)
    else:
        response = requests.get(RNN_SMS_URI)

    result = json.loads(response.text)

    return jsonify(message=result)


@app.route('/')
def index():
    return 'Welcome! use /predict route to POST inputs'

# Comment out code below in production
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
