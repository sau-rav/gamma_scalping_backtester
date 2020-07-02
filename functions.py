import datetime
import calendar
import numpy as np

def roundToNearestInt(val):
    decimal_part = val - int(val)
    if decimal_part <= 0.5:
        return int(val)
    else:
        return int(val) + 1

def getExpiryDate(query_date):
    expiry_dates = [None, 31, 28, 31, 30, 29, 30]
    query_month = query_date.month 
    return datetime.datetime(2020, int(query_month), int(expiry_dates[query_month])).date()

def convertMinutesToDays(query_time):
    total_time = 375
    diff_in_minutes = (query_time.hour - 9) * 60 + query_time.minute - 15
    return diff_in_minutes / total_time

def discountByRate(future_price, rate, curr_date):
    time = (getExpiryDate(curr_date) - curr_date).days / 365 # number of years
    return future_price * np.exp(-rate * time)

def convertTimeToIST(date_obj):
    duration = (5 * 60 + 30) * 60  # in seconds
    delta = datetime.timedelta(seconds = duration)
    date_obj = date_obj + delta
    return date_obj.time()

# d = datetime.datetime.now().date()
# print(getExpiryDate(d))
# print(discountByRate(100, 0.069, datetime.datetime.now().date()))
