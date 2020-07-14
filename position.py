import numpy as np
import datetime
from gamma import *
from requestHandler import *

class Position:
    """


    Parameters :
    

    """
    def __init__(self, id, gamma_object, status, start_iv, start_hv, break_off_vega, max_tolerable_vega, idx):
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
        self.BREAK_OFF_VEGA = break_off_vega
        self.MAX_TOLERABLE_VEGA = max_tolerable_vega

    def evaluate(self, impl_volatility, hist_volatility, vega, i):
        """


        Parameters :
        

        Returns :
        
            
        """
        # check by absolute while exit so as to not abrupt signal changes
        if self.unchartered_territory(impl_volatility, hist_volatility, vega, i):
            self.closePosition(i, impl_volatility, hist_volatility, 'DEVIATION_BREAK_OFF')
        else:
            if self.status == 'SHORT':
                if (impl_volatility - hist_volatility) * vega <= self.BREAK_OFF_VEGA:
                    self.closePosition(i, impl_volatility, hist_volatility, 'VEGA_BREAK_OFF')
            elif self.status == 'LONG':
                if (impl_volatility - hist_volatility) * vega >= -self.BREAK_OFF_VEGA:
                    self.closePosition(i, impl_volatility, hist_volatility, 'VEGA_BREAK_OFF')
            else:
                pnl = self.gamma_scalp.deltaHedge(i)
                if pnl > 0:
                    self.profit_count += 1
                elif pnl < 0:
                    self.loss_count += 1
            self.data_point_indexes.append(i)
       

    def closePosition(self, i, impl_volatility, hist_volatility, close_signal):
        """


        Parameters :
        

        Returns :
        
            
        """
        self.total_pnl = self.gamma_scalp.closePosition(i)
        self.active = False
        writePositionDataToTradeFile(i, self.id, self.status + ' EXIT')
        writeToSummaryFile(self.id, self.entry_time_stamp, getTimeStamp(i), self.status, self.entry_iv, self.entry_hv, impl_volatility, hist_volatility, self.total_pnl, close_signal)
        self.data_point_indexes.append(i)


    def plot(self):
        """


        Parameters :
        

        Returns :
        
            
        """
        # plot the trade data (plotted in dataHnadler function)
        if self.total_pnl >= 0:
            plotTrade(self.id, self.data_point_indexes, 'profit')
        else:
            plotTrade(self.id, self.data_point_indexes, 'loss')


    def unchartered_territory(self, impl_volatility, hist_volatility, vega, i):
        """


        Parameters :
        

        Returns :
        
            
        """
        if self.status == 'SHORT':
            if (impl_volatility - hist_volatility) * vega >= self.MAX_TOLERABLE_VEGA:
                return True
        elif self.status == 'LONG':
            if (impl_volatility - hist_volatility) * vega <= -self.MAX_TOLERABLE_VEGA:
                return True
        return False