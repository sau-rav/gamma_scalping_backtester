import pandas as pd
import numpy as np
import configparser
import datetime
import matplotlib.pyplot as plt
import os
import glob
from pathlib import Path
from functions import *
from bs import *

current_directory = ''
data = pd.DataFrame()
folder_name = ''
# col names :- 
# index,time,timestamp,call_ask_iv,call_bid_iv,put_ask_iv,put_bid_iv,call_ask,call_bid,put_ask,put_bid,call_vega,put_vega,call_delta,put_delta,future_avg,future_ask,future_bid

def initiateDatabase(path_from_main, rolling_wind_size, RISK_FREE_RATE, IV_TOLERENCE):
    # files required for initiating database, all config related data present in config.txt
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path = config.get('Input Data Section', 'data_file_path')
    path = path_from_main

    global data, current_directory, folder_name
    # derive folder for storage from path name (change accordingly)
    folder_name = path.split('_')[2].split('.')[0]

    # for graphical data 
    current_directory = os.getcwd()
    Path(current_directory + '/output/{}/graphs/volatility'.format(folder_name)).mkdir(parents = True, exist_ok = True)
    Path(current_directory + '/output/{}/graphs/vega'.format(folder_name)).mkdir(parents = True, exist_ok = True)
    # remove preexisting files if present
    files = glob.glob(current_directory + '/output/{}/graphs/volatility/*'.format(folder_name))
    for f in files:
        os.remove(f)
    files = glob.glob(current_directory + '/output/{}/graphs/vega/*'.format(folder_name))
    for f in files:
        os.remove(f)
    # read data from file
    data = pd.read_csv(path)
    data.columns = ['time', 'symbol', 'timestamp', 'call_ask_iv', 'call_bid_iv', 'put_ask_iv', 'put_bid_iv', 'call_ask', 'call_bid', 'put_ask', 'put_bid', 'call_vega', 'put_vega', 'call_delta', 'put_delta', 'future_avg', 'future_ask', 'future_bid', 'strike', 'misc1', 'misc2', 'misc3', 'misc4', 'misc5']
    # functions specific to dataset currently in use
    datasetSpecificFunction() # any preprocessing that needs to be done according to structure of dataset

    convertToNumeric() # convert all data to numeric
    STRIKE_PRICE = data.loc[0, 'strike'] # load strike from dataset
    # calculateAvgFuturePrice() # if future avg not calculated
    calculateImpliedVolatility(data.shape[0], STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE)
    calculateHistoricalVolatility(rolling_wind_size, data.shape[0]) 
    calculateVega(data.shape[0], STRIKE_PRICE, RISK_FREE_RATE)
    plotHV_IV()
    plotVega_x_diff()
    return data.shape[0], STRIKE_PRICE, folder_name

def datasetSpecificFunction():
    # removing misc columns
    global data
    data = data.drop(columns = ['time', 'symbol', 'misc1', 'misc2', 'misc3', 'misc4', 'misc5'])
    index = []
    for i in range(data.shape[0]):
        index.append(i+1)
    data['index'] = index
    # print(data.head())

def convertToNumeric():
    # converts string data in all columns to float
    cols = data.columns.drop('timestamp')
    data[cols] = data[cols].apply(pd.to_numeric, errors = 'coerce')

def calculateAvgFuturePrice():
    # adds col for futures average price 
    data['future_avg'] = data[['future_bid', 'future_ask']].mean(axis = 1)

def getSpotPrice(idx, rate, type_of_data):
    # returns spot price for the underlying asset from the data available for future price by discounting
    if type_of_data == 'bid':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'ask':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'avg':
        return discountByRate(data.loc[idx, 'future_avg'], rate, getCurrentDate(idx))

def getSpotPriceFuture(idx, type_of_data):
    # return future price data from the dataset
    if type_of_data == 'bid':
        return data.loc[idx, 'future_bid']
    elif type_of_data == 'ask':
        return data.loc[idx, 'future_ask']
    elif type_of_data == 'avg':
        return data.loc[idx, 'future_avg']

def getOptionPremium(idx, option, type_of_data):
    # returns the option prices (bid, ask, avg) from the dataset
    if option == 'call':
        if type_of_data == 'bid':
            return data.loc[idx, 'call_bid']
        elif type_of_data == 'ask':
            return data.loc[idx, 'call_ask']
        elif type_of_data == 'avg':
            return (data.loc[idx, 'call_bid'] + data.loc[idx, 'call_ask']) / 2
    if option == 'put':
        if type_of_data == 'bid':
            return data.loc[idx, 'put_bid']
        elif type_of_data == 'ask':
            return data.loc[idx, 'put_ask']
        elif type_of_data == 'avg':
            return (data.loc[idx, 'put_bid'] + data.loc[idx, 'put_ask']) / 2

def getHistoricalVolatility(idx):
    # returns the historical volatility at any index from the dataset
    return data.loc[idx, 'historical_volatility']

def getCurrentDate(idx):
    # return current date for timestamp of any index
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    year, month, day = date.split('-')
    return datetime.datetime(int(year), int(month), int(day)).date()

def getCurrentTime(idx):
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    time = data.loc[idx, 'timestamp'].split(' ')[1]
    year, month, day = date.split('-')
    hour, min, sec = time.split(':')
    sec = sec.split('.')[0]
    # res = datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec)).time()
    res = datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec))
    return convertTimeToIST(res)

def getImpliedVolatility(idx):
    # val = data.loc[idx, 'iv_from_dataset']
    val = data.loc[idx, 'implied_volatility']
    return val

def getVega(idx):
    # val = (data.loc[idx, 'call_vega'] + data.loc[idx, 'put_vega']) / 2
    val = data.loc[idx, 'vega']
    return val

def getTimeStamp(idx):
    return data.loc[idx, 'timestamp']

def getDelta(idx, option):
    if option == 'call':
        result = data.loc[idx, 'call_delta']
    if option == 'put':
        result = data.loc[idx, 'put_delta']
    return result

def calculateHistoricalVolatility(rolling_wind_size, dataset_size):
    # calculated the historical volatility by rolling window standard deviation on ln(daily_returns)
    # daily_return = [0] * dataset_size
    # for i in range (0, dataset_size - 1):
    #     daily_return[i] = np.log(data.loc[i, 'future_avg'] / data.loc[i+1, 'future_avg'])
        # daily_return[i] = (data.loc[i, 'future_avg'] / data.loc[i+1, 'future_avg']) - 1
    
    # data['daily_return'] = daily_return
    # data['historical_volatility'] = data['daily_return'].rolling(rolling_wind_size).std() * np.sqrt(252 / (rolling_wind_size / (12 * 24 * 60))) # converted to annual

    # data['historical_volatility'] = (data['implied_volatility']).rolling(rolling_wind_size).median() 
    data['historical_volatility'] = (data['implied_volatility']).ewm(span = rolling_wind_size).mean()

def calculateImpliedVolatility(dataset_size, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE):
    iv_values = []
    for i in range(dataset_size):
        S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
        curr_date = getCurrentDate(i)
        curr_time = getCurrentTime(i)
        T = ((getExpiryDate(curr_date) - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        # T = ((getExpiryDate(curr_date) - curr_date).days + 0.5) / 365 
        C = getOptionPremium(i, 'call', 'avg')
        iv = getImpliedVolatilityBS(C, S, STRIKE_PRICE, T, RISK_FREE_RATE, i, IV_TOLERENCE)
        iv_values.append(iv)
    data['implied_volatility'] = iv_values
    data['implied_volatility'] = data['implied_volatility'].ewm(span = 10).mean() # smootheniing of volatility graph
    data['iv_from_dataset'] = ((data['call_bid_iv'] + data['call_ask_iv'] + data['put_bid_iv'] + data['put_ask_iv']) / 4).ewm(span = 10).mean()

def calculateVega(dataset_size, STRIKE_PRICE, RISK_FREE_RATE):
    vega_values = []
    count = 0
    for i in range(dataset_size):
        S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
        curr_date = getCurrentDate(i)
        curr_time = getCurrentTime(i)
        T = ((getExpiryDate(curr_date) - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        sigma = getImpliedVolatility(i)
        vega = getVegaBS(S, STRIKE_PRICE, T, RISK_FREE_RATE, sigma)
        if float(vega) * float(np.abs(data.loc[i, 'implied_volatility'] - data.loc[i, 'historical_volatility'])) >= 1:
            count += 1
        vega_values.append(vega)
    data['vega'] = vega_values
    # print(count)

def plotVega_x_diff():
    global current_directory, folder_name
    plt.clf()
    plt.plot(data['index'], np.abs(data['implied_volatility'] - data['historical_volatility']) * data['vega'])
    plt.xlabel('index')
    plt.ylabel('vega * diff(HV, IV)')
    plt.savefig(current_directory + '/output/{}/graphs/vega_diff(hv_iv).svg'.format(folder_name), format = 'svg', dpi = 1200)
    plt.clf()
    plt.plot(data['index'], (data['implied_volatility'] - data['historical_volatility']) * data['vega'])
    plt.xlabel('index')
    plt.ylabel('vega * (IV - HV)')
    plt.savefig(current_directory + '/output/{}/graphs/vega_*(iv-hv).svg'.format(folder_name), format = 'svg', dpi = 1200)

def plotHV_IV():
    global current_directory, folder_name
    plt.clf()
    # plt.plot(data['index'], data['iv_from_dataset'], label = 'iv_data', color = 'orange')
    plt.plot(data['index'], data['implied_volatility'], label = 'impl_volatility', color = 'orange')
    plt.plot(data['index'], data['historical_volatility'], label = 'hist_volatility', color = 'blue')
    plt.legend(loc = 'best')
    plt.xlabel('index')
    plt.ylabel('volatility in decimal')
    plt.savefig(current_directory + '/output/{}/graphs/iv_vs_hv.svg'.format(folder_name), format = 'svg', dpi = 1200)
    # plt.show()

def plotTrade(id, indexes, result):
    # trade graphs with volatility
    global current_directory, folder_name
    plt.clf()
    plt.plot(data['index'], data['implied_volatility'], label = 'impl_volatility', color = 'yellow')
    plt.plot(data['index'], data['historical_volatility'], label = 'hist_volatility', color = 'cyan')

    clr = ''
    if result == 'profit':
        clr = 'green'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'implied_volatility'] for i in indexes], color = clr, label = 'profit_trade')
    else:
        clr = 'red'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'implied_volatility'] for i in indexes], color = clr, label = 'loss_trade')
    # plt.plot(data['index'], data['implied_volatility'], label = 'iv_calc', color = 'yellow')
    plt.xlabel('index')
    plt.ylabel('volatility in decimal')
    plt.legend(loc = 'best')
    plt.savefig(current_directory + '/output/{}/graphs/volatility/trade-data{}.svg'.format(folder_name, id), format = 'svg', dpi = 1200)

    # trade graphs with vega x vol_diff
    plt.clf()
    plt.plot(data['index'], (data['vega'] * (data['implied_volatility'] - data['historical_volatility'])), label = 'vega_x_(IV-HV)', color = 'yellow')

    clr = ''
    if result == 'profit':
        clr = 'green'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'vega'] * (data.loc[i, 'implied_volatility'] - data.loc[i, 'historical_volatility']) for i in indexes], color = clr, label = 'profit_trade')
    else:
        clr = 'red'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'vega'] * (data.loc[i, 'implied_volatility'] - data.loc[i, 'historical_volatility']) for i in indexes], color = clr, label = 'loss_trade')
    # plt.plot(data['index'], data['implied_volatility'], label = 'iv_calc', color = 'yellow')
    plt.xlabel('index')
    plt.ylabel('vega_x_diff(HV, IV) in decimal')
    plt.legend(loc = 'best')
    plt.savefig(current_directory + '/output/{}/graphs/vega/trade-data{}.svg'.format(folder_name, id), format = 'svg', dpi = 1200)
    
    


