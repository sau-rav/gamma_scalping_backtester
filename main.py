import configparser
import sys
from gamma import *
from position import *
from dataHandler import *
from functions import *
from requestHandler import * 

config = configparser.ConfigParser()
config.readfp(open(r'config.txt'))

RISK_FREE_RATE = float(config.get('Variable Section', 'rate'))
# STRIKE_PRICE = float(config.get('Variable Section', 'strike_price')) # use strike price from dataset for now
ROLLLING_WINDOW_SIZE = int(config.get('Variable Section', 'rolling_window_size')) # window size on which historical volatility is calculated
SZ_CONTRACT = int(config.get('Variable Section', 'contract_size'))
NUM_CALL = int(config.get('Variable Section', 'num_call_to_trade'))
NUM_PUT = int(config.get('Variable Section', 'num_put_to_trade'))
IV_TOLERENCE = float(config.get('Variable Section', 'iv_tolerence'))
NEG_SIGNAL_TOLERENCE = int(config.get('Variable Section', 'neg_signal_tolerence')) # count of negative signal that will be tolerated, after this reverse position will be taken
SQUARE_OFF_COUNT = int(config.get('Variable Section', 'square_off_count'))
VEGA_x_VOL_MAX = int(config.get('Variable Section', 'vega_max'))
VEGA_x_VOL_MIN = int(config.get('Variable Section', 'vega_min'))
# FIRST_SIGNAL_TOLERENCE = int(config.get('Variable Section', 'first_signal_tolerence'))

# dataset_size = initiateDatabase(ROLLLING_WINDOW_SIZE, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE)
dataset_size, STRIKE_PRICE, folder_name = initiateDatabase(sys.argv[1], ROLLLING_WINDOW_SIZE, RISK_FREE_RATE, IV_TOLERENCE) # load size and strike price from the dataset itself
# dataset_size = ROLLLING_WINDOW_SIZE + 10
openOutputFile(folder_name)

idx = ROLLLING_WINDOW_SIZE // 3
gamma_scalp = None
position_object = None
positions = [] # list of position objects
total_pnl = 0
id = 0

for i in range(idx, dataset_size):
    hist_volatility = getHistoricalVolatility(i) * 100 # in percent format
    impl_volatility = getImpliedVolatility(i) * 100 # in percent format
    vega = getVega(i)

    # parameters 
    S = getSpotPrice(i, RISK_FREE_RATE, 'avg')
    curr_date = getCurrentDate(i)
    T = (getExpiryDate(curr_date) - curr_date).days / 365
    # print("historical volatility {} %, implied volatility {} %".format(hist_volatility, impl_volatility))

    # if reached end then close all position
    if i == dataset_size - 1:
        for position in positions:
            if position.active:
                position.closePosition(i, impl_volatility, hist_volatility)

    # evaluate all positions that are active
    for position in positions:
        if position.active:
            position.evaluate(impl_volatility, hist_volatility, vega, i)
    
    if impl_volatility < hist_volatility and abs(impl_volatility - hist_volatility) * vega > VEGA_x_VOL_MAX: 
        STATUS = 'LONG'
        writePositionDataToTradeFile(idx, id, STATUS + ' START')
        gamma_scalp = GammaScalping('ABC', STRIKE_PRICE, STRIKE_PRICE, T, T, NUM_CALL, NUM_PUT, SZ_CONTRACT, RISK_FREE_RATE, curr_date, STATUS, i, IV_TOLERENCE, id)
        position_object = Position(id, gamma_scalp, STATUS, impl_volatility, hist_volatility, NEG_SIGNAL_TOLERENCE, SQUARE_OFF_COUNT, VEGA_x_VOL_MIN, i)
        positions.append(position_object)
        id += 1

    elif impl_volatility > hist_volatility and abs(impl_volatility - hist_volatility) * vega > VEGA_x_VOL_MAX:
        STATUS = 'SHORT'
        writePositionDataToTradeFile(idx, id, STATUS + ' START')
        gamma_scalp = GammaScalping('ABC', STRIKE_PRICE, STRIKE_PRICE, T, T, NUM_CALL, NUM_PUT, SZ_CONTRACT, RISK_FREE_RATE, curr_date, STATUS, i, IV_TOLERENCE, id)
        position_object = Position(id, gamma_scalp, STATUS, impl_volatility, hist_volatility, NEG_SIGNAL_TOLERENCE, SQUARE_OFF_COUNT, VEGA_x_VOL_MIN, i)
        positions.append(position_object)
        id += 1

closeOutputFile()
profit = 0
loss = 0
countp = 0
countl = 0
for position in positions:
    position.plot()
    total_pnl += position.total_pnl
    if position.total_pnl > 0:
        profit += position.total_pnl
        countp += 1
    else:
        loss += position.total_pnl
        countl += 1

statement_path = './output/statement.csv'
statement_file = open(statement_path, 'a+') # append mode 
statement_file.write("{},{},{},{},{},{},{}\n".format(folder_name,countp+countl, profit, countp, loss, countl, total_pnl))
statement_file.close()