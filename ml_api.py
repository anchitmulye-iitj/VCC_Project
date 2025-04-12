# import random
#
# from fastapi import FastAPI
# import uvicorn
# import numpy as np
# from inference import predict
# from detect_trend import detect_trend
# from pydantic import BaseModel
#
#
# app = FastAPI()
#
# # Dummy initial state
# past_values = [[653], [714], [682], [773], [632], [828], [704], [697], [701], [765]]
# last_prediction = np.array([[745], [731]])
# result_pods = []
#
# # Trend detection parameters (same as before)
# under_t_value = 20
# over_t_value = 2
# CDT_value = 0
# FLAG_value = 0
# n_under_value = 10
# k_under_value = 1.5
# k_std_value = 350
# n_over_value = 20
# k_over_value = 0.6
# request_pod_value = 300
#
#
# class PredictRequest(BaseModel):
#     timestamp: str
#     serviceName: str
#
#
# @app.post("/predict")
# async def serve(data: PredictRequest):
#     global past_values, last_prediction, result_pods, CDT_value, FLAG_value
#
#     # Dummy data for API test
#     dummy_qps_values = np.random.randint(600, 800, size=(120,))  # Random QPS values for 2 mins
#     look_back = 10
#     number = 0
#     previous_pod_num = 0
#
#     for minute in range(1, len(dummy_qps_values) // 60 + 1):
#         current_minute_values = dummy_qps_values[(minute - 1) * 60: minute * 60]
#         avg_qps = np.mean(current_minute_values)
#
#         if minute == 1:
#             past_values.append([715])
#         else:
#             last_minute_avg_qps = np.mean(dummy_qps_values[(minute - 2) * 60: (minute - 1) * 60])
#             past_values.append([last_minute_avg_qps])
#
#         print(f"The past values are {past_values}")
#         prediction = predict(past_values, look_back)
#
#         pred_values = last_prediction.flatten()
#         mean_t_value = avg_qps
#         std_t_value = np.std(current_minute_values)
#
#         data_values = np.array(current_minute_values)
#
#         result, CDT_value, FLAG_value = detect_trend(
#             pred_values, mean_t_value, std_t_value,
#             under_t_value, over_t_value, CDT_value, FLAG_value,
#             n_under_value, k_under_value, k_std_value,
#             n_over_value, k_over_value, request_pod_value,
#             data_values
#         )
#
#         if result == -1 and result_pods:
#             result = result_pods[-1]
#             print(result)
#         number = random.randint(2, 8)
#
#         result_pods.append(number)
#         print(result_pods)
#         last_prediction = prediction
#         previous_pod_num = result_pods[-2] if len(result_pods) >= 2 else None
#
#     return {"current_pod_num": number, "previous_pod_num": previous_pod_num, "timestamp": data.timestamp,
#             "last_prediction": last_prediction.tolist()}
#
#
# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000)
import random

import psycopg2
from fastapi import FastAPI
import uvicorn
import numpy as np
from inference import predict
from detect_trend import detect_trend
from pydantic import BaseModel

# FastAPI app
app = FastAPI()

# Database configuration
DB_CONFIG = {
    'dbname': 'click_logger',
    'user': 'click',
    'password': 'lol007',
    'host': '34.93.76.26',
    'port': '5432'
}

# Initial states
past_values = []
last_prediction = np.array([[745], [731]])
result_pods = []

# Trend detection parameters
under_t_value = 20
over_t_value = 2
CDT_value = 0
FLAG_value = 0
n_under_value = 10
k_under_value = 1.5
k_std_value = 350
n_over_value = 20
k_over_value = 0.6
request_pod_value = 300


class PredictRequest(BaseModel):
    timestamp: str
    serviceName: str


def fetch_data_from_db(timestamp, service_name, limit=10):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # query = "SELECT qps FROM clicks WHERE service_name = %s;"
        # query = "SELECT * FROM clicks;"
        # cur.execute("SELECT * FROM clicks ORDER BY id DESC LIMIT %s;", (limit,))
        cur.execute('SELECT * FROM clicks ORDER BY click_time DESC LIMIT %s;', (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[2] for row in rows]  # Extract qps values as list
    except Exception as e:
        print("Database error:", e)
        return []


@app.post("/predict")
async def serve(data: PredictRequest):
    global past_values, last_prediction, result_pods, CDT_value, FLAG_value

    qps_values = fetch_data_from_db(data.timestamp, data.serviceName)
    print(f"QPS From DB {qps_values}")

    if not qps_values:
        return {"error": "No data found for the given service name"}

    look_back = 10
    avg_qps = np.mean(qps_values)
    std_qps = np.std(qps_values)

    # Maintain past values for prediction
    if len(qps_values) >= 2:
        past_values.append([np.mean(qps_values[:-1])])
    else:
        past_values.append([avg_qps])  # Fallback if data is too short

    prediction = predict(past_values, look_back)
    pred_values = last_prediction.flatten()

    data_values = np.array(qps_values)

    result, CDT_value, FLAG_value = detect_trend(
        pred_values, avg_qps, std_qps,
        under_t_value, over_t_value, CDT_value, FLAG_value,
        n_under_value, k_under_value, k_std_value,
        n_over_value, k_over_value, request_pod_value,
        data_values
    )

    # Simulate pod number decision
    if result == -1 and result_pods:
        result = result_pods[-1]
    print(f"PODS LISR {result_pods}")

    result_pods.append(result)
    last_prediction = prediction

    previous_pod_num = result_pods[-2] if len(result_pods) >= 2 else None
    current_pod_num = result_pods[-1] if len(result_pods) >= 1 else 2
    current_pod_num = random.randint(2, 5)

    return {
        "current_pod_num": current_pod_num,
        "previous_pod_num": previous_pod_num,
        "timestamp": data.timestamp,
        "serviceName": data.serviceName,
        "last_prediction": last_prediction.tolist()
    }


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
