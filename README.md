# Spam Detection API

Spam classifier using LSTM-Recurrent Neural Networks. Deployed using Tensorflow Serving and Flask, built with Docker Compose.
## Dependencies

- Install [docker](https://docs.docker.com/get-docker/) and [docker compose](https://docs.docker.com/compose/install/)
- Install [Python](https://www.python.org/downloads/) 

## Installation

1. Clone repository with `git clone https://github.com/devbcdestiller/spam-detection-api.git`
2. `cd spam-detection-api`
3. `docker-compose build`
4. `docker-compose up`

## Usage

### Retrieve status of an RNN Model

GET `http://localhost:80/v1/status/{model}`  
where {model} is either `sms` or `mail`.  
Returns the status of the model.

### Predict input message

POST `http://localhost:80/v1/predict/{model}`  
where {model} is either `sms` or `mail`.

Request Body

**Content-type:** `form-data` or `application/json`  
| Key           | Required | Value       | Description                      |
|---------------|----------|-------------|----------------------------------|
| input_message | Yes      | text/string | String to be used for inference. |