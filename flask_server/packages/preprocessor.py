from tensorflow import keras
import pickle

# Open tokenizer files
with open('packages/mail_tokenizer.pkl', 'rb') as f:
    token_mail_dict = pickle.load(f)

with open('packages/sms_tokenizer.pkl', 'rb') as f:
    token_sms_dict = pickle.load(f)


# encodes string of text into integers
def encode_message(input_message, tokenizer_dict):
    tokenizer = tokenizer_dict['tokenizer']
    maxlen = tokenizer_dict['max_len']
    message_sequence = tokenizer.texts_to_sequences(input_message)
    encoded_message = keras.preprocessing.sequence.pad_sequences(message_sequence, maxlen=maxlen)

    return encoded_message
