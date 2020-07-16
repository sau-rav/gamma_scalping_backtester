from bs import * 
from dataHandler import *
from functions import *
from gamma import *
from position import *
from requestHandler import *

print('Description of modules present in project\n')

print('automate.py')
print('-------------------------------------------------------------------------------------------------------------------------')
print('For the automated testing of the data this script is used\n')

print('bs.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(getOptionPremiumBS)
help(getImpliedVolatilityBS)
help(getDeltaBS)
help(getGammaBS)
help(getThetaBS)
help(getVegaBS)

print('config.txt')
print('-------------------------------------------------------------------------------------------------------------------------')
print('Config file for setting the parameter value of the model\n')

print('dataHandler.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(initiateDatabase)
help(datasetSpecificFunction)
help(convertToNumeric)
help(calculateAvgFuturePrice)
help(getSpotPrice)
help(getSpotPriceFuture)
help(getOptionPremium)
help(getHistoricalVolatility)
help(getImpliedVolatility)
help(getVega)
help(getDelta)
help(getCurrentDate)
help(getCurrentTime)
help(getTimeStamp)
help(calculateHistoricalVolatility)
help(calculateImpliedVolatility)
help(calculateVega)
help(plotVega_x_diff)
help(plotHV_IV)
help(plotTrade)

print('functions.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(loadExpiryDates)
help(roundToNearestInt)
help(getExpiryDate)
help(convertMinutesToDays)
help(discountByRate)
help(convertTimeToIST)

print('gamma.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(GammaScalping)

print('main.py')
print('-------------------------------------------------------------------------------------------------------------------------')
print('Controls the overall flow of the program\n')

print('position.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(Position)

print('requestHandler.py')
print('-------------------------------------------------------------------------------------------------------------------------')
help(openOutputFile)
help(closeOutputFile)
help(sellRequest)
help(buyRequest)
help(writePositionDataToTradeFile)
help(writeToSummaryFile)

