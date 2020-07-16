import os
import sys
import configparser
from pathlib import Path
from os import listdir
from os.path import isfile, join

expiry_date = []
config = configparser.ConfigParser()
config.readfp(open(r'config.txt'))
expiry_dates_string = config.get('Expiry Date Section', 'exp')
expiry_date.append(None)
for date in expiry_dates_string.split(','):
    expiry_date.append(int(date))

mypath = './dataset/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] # retrive all files in dataset to perform testing on

# open statement file to input the final statement data for the day
current_directory = os.getcwd()
Path(current_directory + '/output').mkdir(parents = True, exist_ok = True)
statement_path = './output/statement.csv'
erase_contents_file = open(statement_path, 'w+') # clear previous data
erase_contents_file.truncate(0)
erase_contents_file.close()
statement_file = open(statement_path, 'a+') # append mode 
statement_file.write("date,total_trades,total_profit,profit_trades,total_loss,loss_trades,overall_pnl(without_TC),option_value_traded,future_value_traded,profit-TC\n")
statement_file.close()

for i in range(0, len(onlyfiles)):
    folder_name = onlyfiles[i].split('_')[2].split('.')[0] # data file name specific function derives the folder name where things needs to be stored
    month = int(folder_name.split('-')[1]) # data file name specific function
    day = int(folder_name.split('-')[2]) # data file name specific function
    if expiry_date[month] == day:
        continue # dont perform for day end as calculation for IV yeilds error
    elif month == 1 and day < 26 and day > 6:
        Path('./output/{}'.format(folder_name)).mkdir(parents = True, exist_ok = True)
        os.system('python3 main.py ./dataset/{}'.format(onlyfiles[i], folder_name))
    elif month == 2 and day < 21 and day > 5:
        Path('./output/{}'.format(folder_name)).mkdir(parents = True, exist_ok = True)
        os.system('python3 main.py ./dataset/{}'.format(onlyfiles[i], folder_name))