import math
from scipy.stats import linregress
import numpy as np


def detect_trend(pred, mean_t, std_t, under_t, over_t, CDT, FLAG, n_under, k_under, k_std, n_over, k_over, request_pod, data):
    # print("Trend detection algorithm in progress============》")
    # print("Current QPS (Queries Per Second)", mean_t)
    # print("Current request fluctuation amplitude ", std_t)
    # print("Predicted results from the LSTM prediction algorithm ", pred)
    pod_t1 = math.ceil(pred[1]/300)
    x = np.arange(60)
    if CDT > 0:
        CDT -= 1
        pod_t1 = -1
    else:
        if under_t > n_under:
            if mean_t < k_under * pred[0] and std_t > k_std:
                FLAG += 1
            else:
                if mean_t > k_under * pred[0] and std_t > k_std:
                    slope, intercept, r_value, p_value, std_err = linregress(x, data)
                    print(slope)
                    if slope >= 1:
                        pod_t1 = (mean_t + std_t) / request_pod
                        print(pod_t1)
                        FLAG = 1
                    else:
                        FLAG = FLAG + 1
                else:
                    if mean_t > k_under * pred[0] and std_t < k_std:
                        CDT = 4
                        FLAG = 0
                        pod_t1 = mean_t / request_pod

            if FLAG == 2:
                pod_t1 = (mean_t + std_t) / request_pod
                CDT = 4
                FLAG = 0
        else:
            FLAG = 0;
        if over_t > n_over:
            if mean_t < k_over * pred[0] and std_t > k_std:
                slope, intercept, r_value, p_value, std_err = linregress(x, data)
                if slope <= -1:
                    CDT = 4
                    pod_t1 = (mean_t + std_t) / request_pod
            else:
                if mean_t < k_over * pred[0] and std_t < k_std:
                    CDT = 4
                    pod_t1 = mean_t / request_pod
    return round(pod_t1), CDT, FLAG

