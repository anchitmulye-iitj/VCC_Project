import numpy as np
from tensorflow.keras.models import load_model
import joblib

# Load model and scaler
model = load_model('lstm_model.h5')
scaler = joblib.load('scaler.save')


def make_single_prediction(model, last_window):
    prediction = model.predict(np.array([last_window]), verbose=0)
    return prediction.flatten()


def predict(past_values, look_back):
    last_window = scaler.transform(np.array(past_values[-look_back:]).reshape(-1, 1))
    prediction = make_single_prediction(model, last_window)
    prediction = scaler.inverse_transform(np.array(prediction).reshape(-1, 1))
    return prediction
