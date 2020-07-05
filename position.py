import numpy as np
import datetime
from gamma import *
from requestHandler import *

class Position:
    def __init__(self, id, gamma_object, status, start_iv, start_hv, neg_signal_tolerence, sqr_off_tolerence, break_off_vega, idx):
        self.active = True
        self.id = id
        self.gamma_scalp = gamma_object
        self.status = status
        self.entry_time_stamp = getTimeStamp(idx)
        self.entry_iv = start_iv
        self.entry_hv = start_hv
        self.sqr_off_count = 0 # square off after this
        self.profit_count = 0 # total points that are profitable on immediate close
        self.loss_count = 0 # total points that are lossy on immediate close
        self.data_point_indexes = [] # for plot purposes
        self.total_pnl = 0 # total pnl at end
        self.NEGATIVE_TOLERENCE = neg_signal_tolerence
        self.SQR_OFF_TOLERENCE = sqr_off_tolerence
        self.BREAK_OFF_VEGA = break_off_vega

    def evaluate(self, impl_volatility, hist_volatility, vega, i):
        # check by absolute while exit so as to not abrupt signal changes
        if self.status == 'SHORT':
            if (impl_volatility - hist_volatility) * vega <= self.BREAK_OFF_VEGA:
                self.closePosition(i, impl_volatility, hist_volatility)
        elif self.status == 'LONG':
            if (impl_volatility - hist_volatility) * vega >= -self.BREAK_OFF_VEGA:
                self.closePosition(i, impl_volatility, hist_volatility)
        else:
            pnl = self.gamma_scalp.deltaHedge(i)
            if pnl > 0:
                self.profit_count += 1
            elif pnl < 0:
                self.loss_count += 1
        self.data_point_indexes.append(i)

    def closePosition(self, i, impl_volatility, hist_volatility):
        self.total_pnl = self.gamma_scalp.closePosition(i)
        self.active = False
        writePositionDataToTradeFile(i, self.id, self.status + ' EXIT')
        writeToSummaryFile(self.id, self.entry_time_stamp, getTimeStamp(i), self.status, self.entry_iv, self.entry_hv, impl_volatility, hist_volatility, self.total_pnl)
        self.data_point_indexes.append(i)

    def plot(self):
        if self.total_pnl >= 0:
            plotTrade(self.id, self.data_point_indexes, 'profit')
        else:
            plotTrade(self.id, self.data_point_indexes, 'loss')

    def analyze(self):
        return self.total_pnl


