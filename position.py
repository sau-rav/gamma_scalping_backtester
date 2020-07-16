import numpy as np
import datetime
from gamma import *
from requestHandler import *

class Position:
    """
    Class definition to construct and monitor position that is taken at any instant

    Parameters :
    id (int) : The id for this position object so that it can be identified uniquely
    gamma_object (Gamma Scalping object) : The underlying gamma scalping object for the position
    status (string) : 'LONG' / 'SHORT' depending on the position which is taken
    start_iv (float) : Implied Volatility value at start of the position
    start_hv (float) : Historical Volatility value at start of the position
    break_off_vega (float) : Value below / above which the position needs to be exited
    max_tolerable_vega (float) : Max value of parameter Vega * (IV - HV) that can be tolerated if the movements of opposite of what we expect
    idx (int) : Index according to the dataset where the position has benn taken

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
        self.futures = abs(gamma_object.total_futures)

    def evaluate(self, impl_volatility, hist_volatility, vega, i):
        """
        Function of evaluate the gamma scalping object of the position at new index, check if hedging is to be performed or the position needs to be closed according to the parameter value

        Parameters :
        impl_volatility (float) : Implied Volatility at the index where evaluation needs to be done
        hist_volatility (float) : Historical Volatilitiy at the index where evaluation needs to be done
        vega (float) : Vega value at the index where evaluation needs to be done
        i (int) : Index according to the dataset where evaluation needs to be done    

        Returns :
        void
            
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
        # if the position is not closed perform delta hedging
        if self.active:
            pnl = self.gamma_scalp.deltaHedge(i)
            if pnl > 0:
                self.profit_count += 1
            elif pnl < 0:
                self.loss_count += 1
            self.data_point_indexes.append(i)
       

    def closePosition(self, i, impl_volatility, hist_volatility, close_signal):
        """
        Function for closing the position by calling close for the gamma scalping object of the position

        Parameters :
        i (int) : Index according to the dataset where evaluation needs to be done
        impl_volatility (float) : Implied Volatility at the index where evaluation needs to be done
        hist_volatility (float) : Historical Volatilitiy at the index where evaluation needs to be done
        close_signal (string) : The reason due to which this position is being closed

        Returns :
        void
            
        """
        self.total_pnl = self.gamma_scalp.closePosition(i)
        self.active = False
        writePositionDataToTradeFile(i, self.id, self.status + ' EXIT')
        writeToSummaryFile(self.id, self.entry_time_stamp, getTimeStamp(i), self.status, self.entry_iv, self.entry_hv, impl_volatility, hist_volatility, self.total_pnl, close_signal)
        self.data_point_indexes.append(i)


    def plot(self):
        """
        Function to plot the trade points for the position

        Parameters :
        (void)

        Returns :
        void
            
        """
        # plot the trade data (plotted in dataHnadler function)
        if self.total_pnl >= 0:
            plotTrade(self.id, self.data_point_indexes, 'profit')
        else:
            plotTrade(self.id, self.data_point_indexes, 'loss')


    def unchartered_territory(self, impl_volatility, hist_volatility, vega, i):
        """
        Function to check if the deviation from expected move if too large and exit the position accordingly

        Parameters :
        impl_volatility (float) : Implied Volatility at the index where checking needs to be done
        hist_volatility (float) : Historical Volatilitiy at the index where checking needs to be done
        vega (float) : Vega value at the index where checking needs to be done
        i (int) : Index according to the dataset where checking needs to be done

        Returns :
        boolean : True if the deviation is too much, False if not
            
        """
        if self.status == 'SHORT':
            if (impl_volatility - hist_volatility) * vega >= self.MAX_TOLERABLE_VEGA:
                return True
        elif self.status == 'LONG':
            if (impl_volatility - hist_volatility) * vega <= -self.MAX_TOLERABLE_VEGA:
                return True
        return False