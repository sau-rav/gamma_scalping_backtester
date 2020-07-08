from dataHandler import *
import configparser
import datetime

path = ""
output_file = None
summary_file = None

def openOutputFile(folder_name):
    config = configparser.ConfigParser()
    config.readfp(open(r'config.txt'))
    global path, output_file, summary_file
    path = config.get('Output Data Section', 'output_file_path')
    # change if folder not required
    path = './output/{}/trade_data.csv'.format(folder_name)
    erase_contents_file = open(path, 'w+') # clear previous data
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    output_file = open(path, 'a+') # append mode 
    output_file.write("idx,position_id,timestamp,action,delta_before,delta_after,delta_change,quantity_traded,PnL_futures,PnL_options,PnL_total\n")

    path = config.get('Output Data Section', 'summary_file_path')
    # change if folder not required
    path = './output/{}/summary_data.csv'.format(folder_name)
    erase_contents_file = open(path, 'w+') # clear previous data
    erase_contents_file.truncate(0)
    erase_contents_file.close()
    summary_file = open(path, 'a+') # append mode
    summary_file.write("position_id,start_timestamp,end_timestamp,position_taken,entry_iv,entry_hv,entry_diff,exit_iv,exit_hv,exit_diff,total_pnl,exit_reason\n")

def closeOutputFile():
    global output_file, summary_file
    output_file.close()
    summary_file.close()

def sellRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current):
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
    output_file.write("{},{},{},sell,{},{},{},{},{},{},{}\n".format(idx, pos_id, curr_time, delta, delta - quantity, -quantity, quantity, profit_on_closing_futures, profit_on_closing_options, total_pnl)) 
    # return necessary details
    if action == 'HEDGE':
        return [price * quantity, total_pnl]
    else:
        return total_pnl

def buyRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current):
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
    output_file.write("{},{},{},buy,{},{},{},{},{},{},{}\n".format(idx, pos_id, curr_time, delta, delta + quantity, quantity, quantity, profit_on_closing_futures, profit_on_closing_options, total_pnl)) 
    # return necessary details
    if action == 'HEDGE':
        return [-price * quantity, total_pnl]
    else:
        return total_pnl

def writePositionDataToTradeFile(idx, pos_id, status):
    curr_time = getTimeStamp(idx)
    output_file.write("{},{},{},{},,,,,,,\n".format(idx, pos_id, curr_time, status))

def writeToSummaryFile(pos_id, start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, exit_iv, exit_hv, total_pnl, close_signal):
    if total_pnl > 0:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pos_id ,start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, close_signal))
    else:
        summary_file.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(pos_id, start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, abs(entry_hv - entry_iv), exit_iv, exit_hv, abs(exit_hv - exit_iv), total_pnl, close_signal))

# openOutputFile()
# closeOutputFile()