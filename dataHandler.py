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

current_directory = '' # name of current directory to save files according to relative path
data = pd.DataFrame()
folder_name = '' # folder name under which summary file, trade file and plots need to be stored inside output folder


def initiateDatabase(ROLLING_WINDOW_SIZE, RISK_FREE_RATE, IV_TOLERENCE, path_from_main):
    """
    Function to initialise the database, drop the non essential columns, process the data to calculate the implied and historical volatility, and create folder for the output of data
    
    Parameters :
    ROLLING_WINDOW_SIZE (int) : Window size on which the historical volatility needs to be calcualted
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)
    IV_TOLERENCE (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
    path_from_main (string) : Path of dataset file for deriving folder name in which dataset needs to be stored in case of automation, NULL in case of running for single file

    Returns : 
    int : Number of rows in dataset (aka size of dataset)
    float : STRIKE_PRICE for the dataset
    string : Folder name in which the summary and trade data needs to be stored under output
        
    """
    # files required for initiating database, all config related data present in config.txt
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    path = config.get('Input Data Section', 'data_file_path') # if single file needs to be run we can provide that file name in config.txt
    if path_from_main != None:
        path = path_from_main # in case of automation.py we need to provide file name as agrument to main and pass it on here for deriving the folder name for output

    global data, current_directory, folder_name
    # derive folder for storage from path name (change accordingly)
    folder_name = path.split('_')[2].split('.')[0] # ****file name specific function (deriving folder name for storage under output from data file name)

    # for graphical data make folder for storing (floder name for storage is derived from data file name above so change if needed)
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
    # functions specific to dataset currently in use
    datasetSpecificFunction() # any preprocessing that needs to be done according to structure of dataset if dataset structure changes this needs to be changed
    convertToNumeric() # convert all data to numeric
    STRIKE_PRICE = data.loc[0, 'strike'] # ****load strike from datasetfor using and returning to main function (change col name if you name strike price column as something else)
    # calculateAvgFuturePrice() # if future avg not calculated calculate future average price
    calculateImpliedVolatility(data.shape[0], STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE) # calculate the implied volatility and smoothen it on window of size 10 
    calculateHistoricalVolatility(data.shape[0], ROLLING_WINDOW_SIZE)  # calculate the historical volatility on specified window size
    calculateVega(data.shape[0], STRIKE_PRICE, RISK_FREE_RATE) # calculate vega for the dataset, not required if already present
    plotHV_IV() # plot of Historical Volatility and Implied volatility v/s index stored in under output in specified folder name
    plotVega_x_diff() # plot of Vega * (IV - HV) v/s index stored in under output in specified folder name
    # return the required data to main
    return data.shape[0], STRIKE_PRICE, folder_name # returning folder name so as to create output folder with name same as data file name


def datasetSpecificFunction():
    """
    This function is specific to the structure of the dataset being used, used to rename the column of the dataset, remove the non required columns and append index to the dataset if not present
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
    # removing misc columns
    global data
    data.columns = ['time', 'symbol', 'timestamp', 'call_ask_iv', 'call_bid_iv', 'put_ask_iv', 'put_bid_iv', 'call_ask', 'call_bid', 'put_ask', 'put_bid', 'call_vega', 'put_vega', 'call_delta', 'put_delta', 'future_avg', 'future_ask', 'future_bid', 'strike', 'misc1', 'misc2', 'misc3', 'misc4', 'misc5']
    data = data.drop(columns = ['time', 'symbol', 'misc1', 'misc2', 'misc3', 'misc4', 'misc5'])
    index = [] # append index if not present in dataset
    for i in range(data.shape[0]):
        index.append(i+1)
    data['index'] = index


def convertToNumeric():
    """
    Convert the data in the dataframe to float values, except the timestamp column, if any other custom column needs to be protected from change to numeric, change this function accordingly
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
    # converts string data in all columns to float
    cols = data.columns.drop('timestamp')
    data[cols] = data[cols].apply(pd.to_numeric, errors = 'coerce')


def calculateAvgFuturePrice():
    """
    Used to calculate the average future price if not present in the dataset
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
    # adds col for futures average price 
    data['future_avg'] = data[['future_bid', 'future_ask']].mean(axis = 1)


def getSpotPrice(idx, rate, type_of_data):
    """
    Retrive the spot price of the underlying asset from the dataset, uses future price from dataset and discounts it over the rate to provide current asset price
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    rate (float) : Risk free rate value in market in decimal (0, 1)
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required

    Returns : 
    float : Price of the underlying asset at given index ('bid', 'ask' or 'avg')
        
    """
    # returns spot price for the underlying asset from the data available for future price by discounting
    if type_of_data == 'bid':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'ask':
        return discountByRate(data.loc[idx, 'future_bid'], rate, getCurrentDate(idx))
    elif type_of_data == 'avg':
        return discountByRate(data.loc[idx, 'future_avg'], rate, getCurrentDate(idx))


def getSpotPriceFuture(idx, type_of_data):
    """
    Retrive the future from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required

    Returns : 
    float : Price of future at given index ('bid', 'ask' or 'avg')
        
    """
    # return future price data from the dataset
    if type_of_data == 'bid':
        return data.loc[idx, 'future_bid']
    elif type_of_data == 'ask':
        return data.loc[idx, 'future_ask']
    elif type_of_data == 'avg':
        return data.loc[idx, 'future_avg']


def getOptionPremium(idx, option, type_of_data):
    """
    Retrive the option premium value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    option (string) : 'call' or 'put' option for which premium needs to be calculated
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required

    Returns : 
    float : Premium of option at given index ('bid', 'ask' or 'avg')
        
    """
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
    """
    Retrive the historical volatility value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    float : Historical Volatility value at given index
        
    """
    # returns the historical volatility at any index from the dataset
    return data.loc[idx, 'historical_volatility']


def getImpliedVolatility(idx):
    """
    Retrive the implied volatility value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    float : Implied Volatility value at given index
        
    """
    # val = data.loc[idx, 'iv_from_dataset']
    val = data.loc[idx, 'implied_volatility']
    return val


def getVega(idx):
    getImpliedVolatility(idx)
    """
    Retrive the vega value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    float : Vega value at given index
        
    """
    # val = (data.loc[idx, 'call_vega'] + data.loc[idx, 'put_vega']) / 2
    val = data.loc[idx, 'vega']
    return val


def getDelta(idx, option):
    """
    Retrive the delta value for an option from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    option (string) : 'call' / 'put' Option for which the delta value is to be calcualted

    Returns : 
    float : Delta value for an option at given index
        
    """
    if option == 'call':
        result = data.loc[idx, 'call_delta']
    if option == 'put':
        result = data.loc[idx, 'put_delta']
    return result


def getCurrentDate(idx):
    """
    Retrive the current date from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    datetime object : Date at the current index in datetime object
        
    """
    # return current date for timestamp of any index
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    year, month, day = date.split('-')
    return datetime.datetime(int(year), int(month), int(day)).date()


def getCurrentTime(idx):
    """
    Retrive the current time from the dataset at given index, use convert to IST if time not present in IST format
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    datetime object : Time at the current index in datetime object
        
    """
    date = data.loc[idx, 'timestamp'].split(' ')[0]
    time = data.loc[idx, 'timestamp'].split(' ')[1]
    year, month, day = date.split('-')
    hour, min, sec = time.split(':')
    sec = sec.split('.')[0]
    res = datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec))
    return convertTimeToIST(res) # convert to IST if time not in IST (else expiration time calculation will yeild bad values)


def getTimeStamp(idx):
    """
    Retrive the current timestamp from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated

    Returns : 
    string : Timestamp at the current index
        
    """
    return data.loc[idx, 'timestamp']


def calculateHistoricalVolatility(dataset_size, rolling_wind_size):
    """
    Calculate and store the historical volatility values for the dataset on rolling window of size provided (Exponential moving average of implied volatility)
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    rolling_wind_size (int) : Size of the rolling window on which historical volatility needs to be calculated

    Returns : 
    void
        
    """
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
    """
    Calculate and store the implied volatility values for the dataset and smoothen it on window of size 10 (Exponential moving average)
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    STRIKE_PRICE (float) : Strike price of the dataset 
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)
    IV_TOLERENCE (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility

    Returns : 
    void
        
    """
    iv_values = []
    for i in range(dataset_size):
        S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
        curr_date = getCurrentDate(i)
        curr_time = getCurrentTime(i)
        T = ((getExpiryDate(curr_date) - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        # T = ((getExpiryDate(curr_date) - curr_date).days + 0.5) / 365 
        C = getOptionPremium(i, 'call', 'avg')
        iv = getImpliedVolatilityBS(C, S, STRIKE_PRICE, T, RISK_FREE_RATE, IV_TOLERENCE)
        iv_values.append(iv)
    data['implied_volatility'] = iv_values
    data['implied_volatility'] = data['implied_volatility'].ewm(span = 10).mean() # smootheniing of volatility graph on window of size 10
    # data['iv_from_dataset'] = ((data['call_bid_iv'] + data['call_ask_iv'] + data['put_bid_iv'] + data['put_ask_iv']) / 4).ewm(span = 10).mean()


def calculateVega(dataset_size, STRIKE_PRICE, RISK_FREE_RATE):
    """
    Calculate and store the vega values for the dataset
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    STRIKE_PRICE (float) : Strike price of the dataset 
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)

    Returns : 
    void
        
    """
    vega_values = []
    for i in range(dataset_size):
        S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
        curr_date = getCurrentDate(i)
        curr_time = getCurrentTime(i)
        T = ((getExpiryDate(curr_date) - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        sigma = getImpliedVolatility(i)
        vega = getVegaBS(S, STRIKE_PRICE, T, RISK_FREE_RATE, sigma)
        vega_values.append(vega)
    data['vega'] = vega_values


def plotVega_x_diff():
    """
    Plot the graph of Vega * (IV - HV) v/s index and store it in dataset specific folder under output 
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
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
    """
    Plot the graph of historical volatility and implied volatility v/s index and store it in dataset specific folder under output 
    
    Parameters :
    (void)

    Returns : 
    void
        
    """
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
    """
    Plot the graph of trade with Vega * (IV - HV) v/s index and with historical and implied volatility v/s index and store it in dataset specific folder under output 
    
    Parameters :
    id (int) : ID of the position for which trade needs to be plotted
    indexes (list) : list of indices according to the dataset which need to be plotted
    result (string) : 'profit' / 'loss' for determining the color with which trade needs to be plotted

    Returns : 
    void
        
    """
    # individual trade graphs with volatility
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
    plt.xlabel('index')
    plt.ylabel('volatility in decimal')
    plt.legend(loc = 'best')
    plt.savefig(current_directory + '/output/{}/graphs/volatility/trade-data{}.svg'.format(folder_name, id), format = 'svg', dpi = 1200)

    # individual trade graphs with vega x vol_diff
    plt.clf()
    plt.plot(data['index'], (data['vega'] * (data['implied_volatility'] - data['historical_volatility'])), label = 'vega_x_(IV-HV)', color = 'yellow')

    clr = ''
    if result == 'profit':
        clr = 'green'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'vega'] * (data.loc[i, 'implied_volatility'] - data.loc[i, 'historical_volatility']) for i in indexes], color = clr, label = 'profit_trade')
    else:
        clr = 'red'
        plt.plot([data.loc[i, 'index'] for i in indexes], [data.loc[i, 'vega'] * (data.loc[i, 'implied_volatility'] - data.loc[i, 'historical_volatility']) for i in indexes], color = clr, label = 'loss_trade')
    plt.xlabel('index')
    plt.ylabel('vega_x_diff(HV, IV) in decimal')
    plt.legend(loc = 'best')
    plt.savefig(current_directory + '/output/{}/graphs/vega/trade-data{}.svg'.format(folder_name, id), format = 'svg', dpi = 1200)
