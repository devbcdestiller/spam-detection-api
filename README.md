# Spam Detection API

Spam classifier using LSTM-Recurrent Neural Networks. Deployed using Tensorflow Serving and Flask, built with Docker Compose.

## Usage

### Retrieve status of a Model

GET `/v1/status/{model}`  
where {model} is either `sms` or `mail`.  
Returns the status of the model.

### Predict input message

POST `/v1/predict/{model}`  
where {model} is either `sms` or `mail`.

Request Body

**Content-type:** `form-data` or `application/json`  
| Key           | Required | Value       | Description                      |
|---------------|----------|-------------|----------------------------------|
| input_message | Yes      | text/string | String to be used for inference. |  

Returns the result of the prediction in JSON.  
| Key            | Value       | Description                      |
|---------------|-------------|----------------------------------|
| classification | text/string | ham or spam |
| message | text/string | The request `input_message`. |
| model | text/string | Model used for prediction. `sms` or `mail` |
| spam_percent | float | Probability that the input_message is spam. |

### Batch prediction

POST `/v1/predict/batch/{model}`  
where {model} is either `sms` or `mail`.

Request Body

**Content-type:** `form-data` or `application/json`  
| Key           | Required | Value       | Description                      |
|---------------|----------|-------------|----------------------------------|
| input_messages | Yes      | array | Array of strings to be used for inference. |  

Returns the result of the prediction in JSON.  
| Key            | Value       | Description                      |
|---------------|-------------|----------------------------------|
| length | integer | Length of the `predictions`.  |
| model | text/string | Model used for prediction. `sms` or `mail` |
| predictions | array | Array of objects containing the result for each inference. |
| message | text/string | The request `input_messages`. |
| spam_percent | float | Probability that the message is spam. |
