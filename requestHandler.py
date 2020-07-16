from dataHandler import *
import configparser
import datetime

trade_data_file = None # file object for writing trade data
summary_file = None # file object for writing summary data


def openOutputFile(folder_name):
    """
    Function to initiate file objects for writing trade data and summary data
    
    Parameters : 
    folder_name (string) : name of folder under which the summary file, trade data file and plots needs to be placed

    Returns : 
    void

    """
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    global trade_data_file, summary_file

    file_name = config.get('Output Data Section', 'trade_data_file_name') # get file name for storing trade data
    path = './output/{}/{}'.format(folder_name, file_name)
    erase_contents_file = open(path, 'w+') # clear previous data if any
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    trade_data_file = open(path, 'a+') # open file in append mode for writing the trade data
    trade_data_file.write("idx,position_id,timestamp,action,delta_before,delta_after,delta_change,quantity_traded,PnL_futures,PnL_options,PnL_total\n")

    file_name = config.get('Output Data Section', 'summary_file_name') # get file name for storing summary data
    path = './output/{}/{}'.format(folder_name, file_name)
    erase_contents_file = open(path, 'w+') # clear previous data if any
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    summary_file = open(path, 'a+') # open file in append mode for writing the summary data
    summary_file.write("position_id,start_timestamp,end_timestamp,position_taken,entry_iv,entry_hv,entry_diff,exit_iv,exit_hv,exit_diff,total_pnl,exit_reason\n")


def closeOutputFile():
    """
    Function to close the files opened for writing the trade and summary data
    
    Parameters : 
    (void)

    Returns : 
    void
    
    """
    global trade_data_file, summary_file
    trade_data_file.close()
    summary_file.close()


def sellRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current):
    """
    Function to sell the specified quantity of asset and return the balance change of futures, also calculates the total PnL if the position is closed at current index
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    action (string) : Action to be performed ('EXIT' / 'HEDGE')
    quantity (int) : Quantity of the asset to be sold
    idx (int) : Index of the dataset file(row number) for which request needs to be evaluated
    total_futures (int) : Amount of futures currently in hand
    future_balance (float) : Net balance of futures currently in hand
    option_balance_init (float) : Option net balance when the position was initialised
    option_balance_current (float) : Option net balance at current index

    Returns : 
    if action == 'HEDGE'
    float : Balance change in futures by selling specified quantity at current market price (at current index)
    float : Total PnL if this position was closed at current index

    if action == 'EXIT'
    float : Total PnL after closing this position at current index
    float : Balance change in futures by buying specified quantity at current market price (at current index)

    """
    price = getSpotPriceFuture(idx, 'bid')
    curr_time = getTimeStamp(idx)
    # change in quantities
    future_balance += price * quantity
    total_futures -= quantity
    # profit on closing futures position
    profit_on_closing_futures = 0
    if total_futures > 0:
        profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'bid') * total_futures
    elif total_futures < 0:
        profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'ask') * total_futures
    else:
        profit_on_closing_futures = future_balance
    # profit on closing options position
    profit_on_closing_options = option_balance_current + option_balance_init
    # total pnl
    total_pnl = profit_on_closing_futures + profit_on_closing_options
    # write to file
    trade_data_file.write("{},{},{},sell,{},{},{},{},{},{},{}\n".format(idx, pos_id, curr_time, delta, delta - quantity, -quantity, quantity, profit_on_closing_futures, profit_on_closing_options, total_pnl)) 
    # return necessary details
    if action == 'HEDGE':
        return [price * quantity, total_pnl]
    else:
        return [total_pnl, price * quantity]


def buyRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current):
    """
    Function to buy the specified quantity of asset and return the balance change of futures, also calculates the total PnL if the position is closed at current index
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    action (string) : Action to be performed ('EXIT' / 'HEDGE')
    quantity (int) : Quantity of the asset to be bought
    idx (int) : Index of the dataset file(row number) for which request needs to be evaluated
    total_futures (int) : Amount of futures currently in hand
    future_balance (float) : Net balance of futures currently in hand
    option_balance_init (float) : Option net balance when the position was initialised
    option_balance_current (float) : Option net balance at current index

    Returns : 
    if action == 'HEDGE'
    float : Balance change in futures by buying specified quantity at current market price (at current index)
    float : Total PnL if this position was closed at current index

    if action == 'EXIT'
    float : Total PnL after closing this position at current index
    float : Balance change in futures by buying specified quantity at current market price (at current index)

    """
    price = getSpotPriceFuture(idx, 'ask')
    curr_time = getTimeStamp(idx)
    # change in quantities
    future_balance -= price * quantity
    total_futures += quantity
    # profit on closing futures position
    profit_on_closing_futures = 0
    if total_futures > 0:
        profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'bid') * total_futures
    elif total_futures < 0:
        profit_on_closing_futures = future_balance + getSpotPriceFuture(idx, 'ask') * total_futures
    else:
        profit_on_closing_futures = future_balance
    # profit on closing options position
    profit_on_closing_options = option_balance_current + option_balance_init
    # total pnl
    total_pnl = profit_on_closing_futures + profit_on_closing_options
    # write the trade to file
    trade_data_file.write("{},{},{},buy,{},{},{},{},{},{},{}\n".format(idx, pos_id, curr_time, delta, delta + quantity, quantity, quantity, profit_on_closing_futures, profit_on_closing_options, total_pnl)) 
    # return necessary details
    if action == 'HEDGE':
        return [-price * quantity, total_pnl]
    else:
        return [total_pnl, price * quantity]


def writePositionDataToTradeFile(idx, pos_id, status):
    """
    Function to write position opening and closing data to trade file
    
    Parameters : 
    idx (int) : Current index according to dataset for which the data is to be written
    pos_id (int) : Position ID for the gamma scalping object
    status (string) : 'LONG START / SHORT START / LONG EXIT / SHORT EXIT' depending on the position taken / closed

    Returns : 
    void

    """
    curr_time = getTimeStamp(idx)
    trade_data_file.write("{},{},{},{},,,,,,,\n".format(idx, pos_id, curr_time, status))


def writeToSummaryFile(pos_id, start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, exit_iv, exit_hv, total_pnl, close_signal):
    """
    Function to write the summary for the position, the entry timestamp, exit timestamp, entry IV, exit IV, entry HV, exit HV, total PnL etc.
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    start_timestamp (string) : Start timestamp for the position
    end_timestamp (string) : End timestamp for the position
    entry_iv (float) : Implied Volatility when the position was initiated
    entry_hv (float) : Historical Volatility when the position was initiated
    exit_iv (float) : Implied Volatility when the postition was closed
    exit_hv (float) : Historical Volatility when the position was closed
    total_pnl (float) : Total profit / loss encountered from this position
    close_signal (string) : Reason for which the position was closed

    Returns : 
    void

    """
    if total_pnl > 0:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pos_id ,start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, close_signal))
    else:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pos_id, start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, close_signal))
