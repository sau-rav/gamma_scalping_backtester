import numpy as np
import datetime
from bs import *
from dataHandler import *
from requestHandler import *
from functions import *

class GammaScalping:
    """
    Class definition to construct and monitor gamma scalping object
    
    Parameters :
    symbol (string) : The symbol of the asset which is under consideration
    call_strike (float) : Strike price of call option bought / sold
    put_strike (float) : Strike price of put option bought / sold
    call_expiry (float) : Time till expiration of call option expressed in years
    put_expiry (float) : Time till expiration of put option expressed in years
    num_contracts_call (int) : number of contracts of call bought / sold
    num_contracts_put (int) : number of contracts of put bought / sold
    contr_size (int) : Contract size of the asset
    risk_free_rate (float) : Risk free rate in market in decimal (0, 1)
    curr_date (datetime) : Date on which object was initialised
    gamma_position (string) : 'LONG' / 'SHORT' Position which is taken
    init_idx (int) : Index according to the database on which object was initialised
    iv_tol (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
    pos_id (int) : Position ID for the gamma_scalp object (id of position under which this object was initialised)
    
    option_value_traded (float) : Total amount of option value traded for calculation of transaction cost
    future_valur_traded (float) : Total amount of future value traded for calculation of transaction cost 
        
    """
    def __init__(self, symbol, call_strike, put_strike, call_expiry, put_expiry, num_contracts_call, num_contracts_put, contr_size, risk_free_rate, curr_date, gamma_position, init_idx, iv_tol, pos_id):
        self.s_symbol = symbol
        self.pos_id = pos_id
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
        self.delta_tolerence = 1.5
        self.option_value_traded = abs(self.option_balance_initial)
        self.future_value_traded = 0
        self.deltaHedge(init_idx)

    def optionBalanceHelperFunction(self, idx, signal):
        """
        Function to find option balance at given index, helps to find out the profit / loss if the option position is closed at current index
        
        Parameters :
        idx (int) : Index according to the dataset where the balance of the options need to be evaluated
        signal (string) : 'ENTER' / 'EXIT' depending on for whether the balance needs to be calculated for entry into position or exit from the position

        Returns : 
        float : Balance of options in hand for the specified signal

        """
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


    def getOptionsCurrentCost(self, idx, type_of_price):
        """
        Extraction of premium for the call and put option from the dataset 

        Parameters :
        idx (int) : Index according to the dataset for which the call and put premium needs to be evaluated
        type_of_price (string) : 'bid', 'ask' or 'avg' according to which type of price is required

        Returns :
        float : Option premium sum for all calls and puts in hand
            
        """
        call_premium = getOptionPremium(idx, 'call', type_of_price)
        put_premium = getOptionPremium(idx, 'put', type_of_price)

        bal = call_premium * self.c_contracts * self.contract_size + put_premium * self.p_contracts * self.contract_size
        return bal


    def calcDelta(self, idx):
        """
        Used to calculate delta for the position (for this particular gamma_scalp object)

        Parameters :
        idx (int) : Index according to the dataset for which delta needs to be calculated

        Returns :
        float : Delta value for the position
            
        """
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
        """
        Used to calculate delta, check if delta is away from zero and perform buying and selling to bring delta close to zero

        Parameters :
        idx (int) : Index according to the dataset for which delta hedging needs to be done

        Returns :
        float : Total profit or loss if the position is closed at given index
            
        """
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
            self.future_value_traded += abs(balance_change)
            delta -= sell_quantity
        elif delta < 0 - self.delta_tolerence:
            # initiate buy request
            buy_quantity = roundToNearestInt(-delta)
            [balance_change, total_pnl] = buyRequest(self.pos_id, 'HEDGE', buy_quantity, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
            self.future_balance += balance_change
            self.total_futures += buy_quantity
            self.future_value_traded += abs(balance_change)
            delta += buy_quantity
        return total_pnl


    def closePosition(self, idx):
        """
        Used for closing the position

        Parameters :
        idx (int) : Index according to the dataset for where position needs to be closed

        Returns :
        float : Total profit / loss after closing the position
            
        """
        self.updateTimeTillExpiration(idx)
        delta = self.calcDelta(idx)
        option_balance_current = self.optionBalanceHelperFunction(idx, 'EXIT')
        self.option_value_traded += abs(option_balance_current)

        total_pnl = 0
        if self.total_futures > 0:
            [total_pnl, value_traded] = sellRequest(self.pos_id, 'EXIT', self.total_futures, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
        else: 
            [total_pnl, value_traded] = buyRequest(self.pos_id, 'EXIT', -self.total_futures, idx, delta, self.total_futures, self.future_balance, self.option_balance_initial, option_balance_current)
        self.future_value_traded += abs(value_traded)
        return total_pnl


    def updateTimeTillExpiration(self, idx):
        """
        Used to update time till expitation for the call option and put option expiry, which is used later for delta calculation

        Parameters :
        idx (int) : Index according to the dataset which needs to be accounted for time update

        Returns :
        void
            
        """
        curr_date = getCurrentDate(idx)
        curr_time = getCurrentTime(idx)
        self.c_expiry = ((self.c_expiry_date - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365
        self.p_expiry = ((self.p_expiry_date - curr_date).days + 1 - convertMinutesToDays(curr_time)) / 365

    
    


