import numpy as np
import datetime
from bs import *
from dataHandler import *
from requestHandler import *
from functions import *

class GammaScalping:
    def __init__(self, symbol, call_strike, put_strike, call_expiry, put_expiry, num_contracts_call, num_contracts_put, contr_size, risk_free_rate, curr_date, gamma_position, init_idx, iv_tol, pos_id):
        self.s_symbol = symbol
        self.start_timestamp = getTimeStamp(init_idx)
        self.c_strike = call_strike # strike price of put option
        self.p_strike = put_strike # strike price of call option
        self.c_expiry = call_expiry # time till expiration of call expressed in years
        self.p_expiry = put_expiry # time till expiration of put expressed in years
        self.c_expiry_date = getExpiryDate(curr_date)
        self.p_expiry_date = getExpiryDate(curr_date)
        self.contract_size = contr_size
        self.c_contracts = num_contracts_call  # a contract contains of contract_size options (of the type call or put)
        self.p_contracts = num_contracts_put
        self.rate = risk_free_rate 
        self.g_position = gamma_position # gamma position is LONG(LONG gamma) or SHORT(SHORT gamma)
        self.option_balance_initial = self.optionBalanceHelperFunction(init_idx, 'ENTER') # take bid or ask price according to position while entering into the position
        self.total_futures = 0 # total number of futures in hand, will hedge using futures
        self.future_balance = 0 
        self.delta_tolerence = 0.5
        self.pos_id = pos_id
        self.deltaHedge(init_idx)

    def optionBalanceHelperFunction(self, idx, signal):
        if signal == 'ENTER':
            if self.g_position == 'LONG':
                return -self.getOptionsCurrentCost(idx, 'ask')
            elif self.g_position == 'SHORT':
                return self.getOptionsCurrentCost(idx, 'bid')
        elif signal == 'EXIT':
            if self.g_position == 'LONG':
                return self.getOptionsCurrentCost(idx, 'bid')
            elif self.g_position == 'SHORT':
                return -self.getOptionsCurrentCost(idx, 'ask')

    def getOptionsCurrentCost(self, init_idx, type_of_price):
        call_premium = getOptionPremium(init_idx, 'call', type_of_price)
        put_premium = getOptionPremium(init_idx, 'put', type_of_price)

        bal = call_premium * self.c_contracts * self.contract_size + put_premium * self.p_contracts * self.contract_size
        return bal

    def calcDelta(self, idx):
        spot_price = getSpotPrice(idx, self.rate, 'avg') # mid price of bid ask
        sigma = getImpliedVolatility(idx)
        # C = getOptionPremium(idx, 'call', 'avg')
        # sigma = getImpliedVolatilityBS(C, spot_price, self.c_strike, self.c_expiry, self.rate, idx, self.iv_tolerence) 

        # call_delta = getDelta(idx, 'call')
        call_delta = getDeltaBS(spot_price, self.c_strike, self.c_expiry, self.rate, sigma, 'call') 
        assert call_delta <= 1 and call_delta >= 0, 'Call delta not in range error'
        # print("call delta : {}".format(call_delta)) # apply checks -> applied
        
        # put_delta = getDelta(idx, 'put')
        put_delta = getDeltaBS(spot_price, self.p_strike, self.p_expiry, self.rate, sigma, 'put') 
        assert put_delta <= 0 and put_delta >= -1, 'Put delta not in range error'
        # print("put delta : {}".format(put_delta))

        delta_value = 0
        if self.g_position == 'LONG':
            delta_value = self.total_futures + call_delta * self.c_contracts * self.contract_size + put_delta * self.p_contracts * self.contract_size
        elif self.g_position == 'SHORT':
            delta_value = self.total_futures - call_delta * self.c_contracts * self.contract_size - put_delta * self.p_contracts * self.contract_size
        return delta_value

    def deltaHedge(self, idx):
        # updating c_expiry, p_expiry according to currdate and curr time
        self.updateTimeTillExpiration(idx)

        # print("-----------Performing hedging.. at idx = {} timestamp : {} ------------".format(idx, getTimeStamp(idx)))
        delta = self.calcDelta(idx)
        option_balance_current = self.optionBalanceHelperFunction(idx, 'EXIT')
        total_pnl = 0
        
        if delta > 0 + self.delta_tolerence:
            # initiate sell request
            sell_quantity = roundToNearestInt(delta)
            [balance_change, total_pnl] = sellRequest(self.pos_id, 'HEDGE', sell_quantity, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
            self.future_balance += balance_change
            self.total_futures -= sell_quantity
            delta -= sell_quantity
        elif delta < 0 - self.delta_tolerence:
            # initiate buy request
            buy_quantity = roundToNearestInt(-delta)
            [balance_change, total_pnl] = buyRequest(self.pos_id, 'HEDGE', buy_quantity, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
            self.future_balance += balance_change
            self.total_futures += buy_quantity
            delta += buy_quantity
        return total_pnl

    def closePosition(self, idx):
        self.updateTimeTillExpiration(idx)
        delta = self.calcDelta(idx)
        option_balance_current = self.optionBalanceHelperFunction(idx, 'EXIT')

        total_pnl = 0
        if self.total_futures > 0:
            total_pnl = sellRequest(self.pos_id, 'EXIT', self.total_futures, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
        else: 
            total_pnl = buyRequest(self.pos_id, 'EXIT', -self.total_futures, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
        return total_pnl

    def updateTimeTillExpiration(self, idx):
        curr_date = getCurrentDate(idx)
        curr_time = getCurrentTime(idx)
        self.c_expiry = ((self.c_expiry_date - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        self.p_expiry = ((self.p_expiry_date - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365

    
    


