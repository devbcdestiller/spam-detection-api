#!/bin/bash

tensorflow_model_server --port=8502 --rest_api_port=8503 --model_name="${MODEL_NAME}" --model_base_path="${MODEL_BASE_PATH}"/"${MODEL_NAME}" "$@"
