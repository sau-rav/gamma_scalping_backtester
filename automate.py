import os
import sys
from pathlib import Path
from os import listdir
from os.path import isfile, join

expiry_date = [None, 31, 28, 31, 30, 29, 30]
mypath = './dataset/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

statement_path = './output/statement.csv'
erase_contents_file = open(statement_path, 'w+') # clear previous data
erase_contents_file.truncate(0)
erase_contents_file.close()

statement_file = open(statement_path, 'a+') # append mode 
statement_file.write("date,total_trades,total_profit,profit_trades,total_loss,loss_trades,overall\n")
statement_file.close()

for i in range(0, len(onlyfiles)):
    file_name = onlyfiles[i].split('_')[2].split('.')[0]
    month = int(file_name.split('-')[1])
    day = int(file_name.split('-')[2])
    if expiry_date[month] == day:
        continue
    elif month == 1 and day < 25:
        print('Evaluating for {}'.format(file_name))
        Path('./output/{}'.format(file_name)).mkdir(parents = True, exist_ok = True)
        os.system('python3 main.py ./dataset/{}'.format(onlyfiles[i], file_name))
    elif month == 2 and day < 21 and day > 5:
        print('Evaluating for {}'.format(file_name))
        Path('./output/{}'.format(file_name)).mkdir(parents = True, exist_ok = True)
        os.system('python3 main.py ./dataset/{}'.format(onlyfiles[i], file_name))