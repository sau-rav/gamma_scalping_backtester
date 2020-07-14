import datetime
import calendar
import configparser
import numpy as np

expiry_dates = [] # expiry dates for various months

def loadExpiryDates():
    """
    Loads the expiry dates for all months from the config file
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    global expiry_dates
    expiry_dates_string = config.get('Expiry Date Section', 'exp')
    expiry_dates.append(None)
    for date in expiry_dates_string.split(','):
        expiry_dates.append(int(date))


def roundToNearestInt(val):
    """
    Rounds off the value to nearest integer value
    
    Parameters :
    val (float) : Value which needs to be rounded off

    Returns : 
    int : Value rounded off to nearest integer
        
    """
    decimal_part = val - int(val)
    if decimal_part <= 0.5:
        return int(val)
    else:
        return int(val) + 1


def getExpiryDate(query_date):
    """
    Retrieve the expiry date for the query date
    
    Parameters :
    query_date (datetime object) : Date for which expiry date needs to be returned

    Returns : 
    datetime object : Expiry date for the queried date
        
    """
    global expiry_dates
    query_month = query_date.month 
    return datetime.datetime(2020, int(query_month), int(expiry_dates[query_month])).date()


def convertMinutesToDays(query_time):
    """
    Returns the time remaining(in days) for the current day to end in decimal
    
    Parameters :
    query_time (datetime object) : Time for which the time remaining until dayend(in days) needs to be calculated in decimal

    Returns : 
    float : Time remaining until the day end (in days according to current time)
        
    """
    total_time = 375
    diff_in_minutes = (query_time.hour - 9) * 60 + query_time.minute - 15
    return diff_in_minutes / total_time


def discountByRate(future_price, rate, curr_date):
    """
    Returns the discounted price according to provided rate and time, used to calculate stock price from future price
    
    Parameters :
    future_price (float) : Price of future currently
    rate (float) : Risk free rate in market in decimal (0, 1)
    curr_date (datetime object) : Current date to calculate time remaing for which disount is to be done

    Returns : 
    float : Future price discounted on given rate for given time till expiry
        
    """
    time = (getExpiryDate(curr_date) - curr_date).days / 365 # number of years
    return future_price * np.exp(-rate * time)


def convertTimeToIST(date_obj):
    """
    Function to convert the given time to IST

    Parameters :
    date_obj (datetime object) : The datetime object which needs to be convereted to IST

    Returns : 
    datetime object : The input converted to IST
        
    """
    duration = (5 * 60 + 30) * 60  # in seconds
    delta = datetime.timedelta(seconds = duration)
    date_obj = date_obj + delta
    return date_obj.time()