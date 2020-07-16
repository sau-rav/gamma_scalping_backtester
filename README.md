Description of modules present in project

automate.py
-------------------------------------------------------------------------------------------------------------------------
For the automated testing of the data this script is used

bs.py
-------------------------------------------------------------------------------------------------------------------------
Help on function getOptionPremiumBS in module bs:

getOptionPremiumBS(S, K, T, r, sigma, option)
    Function to calculate option premium value using Black Scholes model
    
    Parameters : 
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    sigma (float) : Implied Volatility
    option ('call' / 'put') : Type of option for which calculation is to be done
    
    Returns : 
    float : Premium of the option for given parameter values

Help on function getImpliedVolatilityBS in module bs:

getImpliedVolatilityBS(C, S, K, T, r, precision)
    Function to calculate implied volatility value using binary search on interval [0, 2]
    
    Parameters :
    C (float) : Call option premium 
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    precision (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
    
    Returns : 
    float : Implied Volatility for given parameter values

Help on function getDeltaBS in module bs:

getDeltaBS(S, K, T, r, sigma, option)
    Function to calculate option's delta value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility
    option ('call' / 'put') : Type of option for which calculation is to be done
    
    Returns : 
    float : Delta of option for given parameter values

Help on function getGammaBS in module bs:

getGammaBS(S, K, T, r, sigma)
    Function to calculate option's gamma value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility
    
    Returns : 
    float : Gamma of option for given parameter values

Help on function getThetaBS in module bs:

getThetaBS(S, K, T, r, sigma, option, days)
    Function to calculate option's theta value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility
    option ('call' / 'put') : Type of option for which calculation is to be done
    days : Number of trading days in a year (252)
    
    Returns : 
    float : Theta of option for given parameter values

Help on function getVegaBS in module bs:

getVegaBS(S, K, T, r, sigma)
    Function to calculate option's vega value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility
    
    Returns : 
    float : Delta of option for given parameter values

config.txt
-------------------------------------------------------------------------------------------------------------------------
Config file for setting the parameter value of the model

dataHandler.py
-------------------------------------------------------------------------------------------------------------------------
Help on function initiateDatabase in module dataHandler:

initiateDatabase(ROLLING_WINDOW_SIZE, RISK_FREE_RATE, IV_TOLERENCE, path_from_main)
    Function to initialise the database, drop the non essential columns, process the data to calculate the implied and historical volatility, and create folder for the output of data
    
    Parameters :
    ROLLING_WINDOW_SIZE (int) : Window size on which the historical volatility needs to be calcualted
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)
    IV_TOLERENCE (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
    path_from_main (string) : Path of dataset file for deriving folder name in which dataset needs to be stored in case of automation, NULL in case of running for single file
    
    Returns : 
    int : Number of rows in dataset (aka size of dataset)
    float : STRIKE_PRICE for the dataset
    string : Folder name in which the summary and trade data needs to be stored under output

Help on function datasetSpecificFunction in module dataHandler:

datasetSpecificFunction()
    This function is specific to the structure of the dataset being used, used to rename the column of the dataset, remove the non required columns and append index to the dataset if not present
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function convertToNumeric in module dataHandler:

convertToNumeric()
    Convert the data in the dataframe to float values, except the timestamp column, if any other custom column needs to be protected from change to numeric, change this function accordingly
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function calculateAvgFuturePrice in module dataHandler:

calculateAvgFuturePrice()
    Used to calculate the average future price if not present in the dataset
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function getSpotPrice in module dataHandler:

getSpotPrice(idx, rate, type_of_data)
    Retrive the spot price of the underlying asset from the dataset, uses future price from dataset and discounts it over the rate to provide current asset price
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    rate (float) : Risk free rate value in market in decimal (0, 1)
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required
    
    Returns : 
    float : Price of the underlying asset at given index ('bid', 'ask' or 'avg')

Help on function getSpotPriceFuture in module dataHandler:

getSpotPriceFuture(idx, type_of_data)
    Retrive the future from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required
    
    Returns : 
    float : Price of future at given index ('bid', 'ask' or 'avg')

Help on function getOptionPremium in module dataHandler:

getOptionPremium(idx, option, type_of_data)
    Retrive the option premium value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    option (string) : 'call' or 'put' option for which premium needs to be calculated
    type_of_data (string) : 'bid', 'ask' or 'avg' according to which type of price is required
    
    Returns : 
    float : Premium of option at given index ('bid', 'ask' or 'avg')

Help on function getHistoricalVolatility in module dataHandler:

getHistoricalVolatility(idx)
    Retrive the historical volatility value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    
    Returns : 
    float : Historical Volatility value at given index

Help on function getImpliedVolatility in module dataHandler:

getImpliedVolatility(idx)
    Retrive the implied volatility value from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    
    Returns : 
    float : Implied Volatility value at given index

Help on function getVega in module dataHandler:

getVega(idx)

Help on function getDelta in module dataHandler:

getDelta(idx, option)
    Retrive the delta value for an option from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    option (string) : 'call' / 'put' Option for which the delta value is to be calcualted
    
    Returns : 
    float : Delta value for an option at given index

Help on function getCurrentDate in module dataHandler:

getCurrentDate(idx)
    Retrive the current date from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    
    Returns : 
    datetime object : Date at the current index in datetime object

Help on function getCurrentTime in module dataHandler:

getCurrentTime(idx)
    Retrive the current time from the dataset at given index, use convert to IST if time not present in IST format
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    
    Returns : 
    datetime object : Time at the current index in datetime object

Help on function getTimeStamp in module dataHandler:

getTimeStamp(idx)
    Retrive the current timestamp from the dataset at given index
    
    Parameters :
    idx (int) : Index value according to the dataset for which the query has been initiated
    
    Returns : 
    string : Timestamp at the current index

Help on function calculateHistoricalVolatility in module dataHandler:

calculateHistoricalVolatility(dataset_size, rolling_wind_size)
    Calculate and store the historical volatility values for the dataset on rolling window of size provided (Exponential moving average of implied volatility)
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    rolling_wind_size (int) : Size of the rolling window on which historical volatility needs to be calculated
    
    Returns : 
    void

Help on function calculateImpliedVolatility in module dataHandler:

calculateImpliedVolatility(dataset_size, STRIKE_PRICE, RISK_FREE_RATE, IV_TOLERENCE)
    Calculate and store the implied volatility values for the dataset and smoothen it on window of size 10 (Exponential moving average)
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    STRIKE_PRICE (float) : Strike price of the dataset 
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)
    IV_TOLERENCE (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
    
    Returns : 
    void

Help on function calculateVega in module dataHandler:

calculateVega(dataset_size, STRIKE_PRICE, RISK_FREE_RATE)
    Calculate and store the vega values for the dataset
    
    Parameters :
    dataset_size (int) : Number of rows in the dataset
    STRIKE_PRICE (float) : Strike price of the dataset 
    RISK_FREE_RATE (float) : Risk free rate in market in decimal (0, 1)
    
    Returns : 
    void

Help on function plotVega_x_diff in module dataHandler:

plotVega_x_diff()
    Plot the graph of Vega * (IV - HV) v/s index and store it in dataset specific folder under output 
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function plotHV_IV in module dataHandler:

plotHV_IV()
    Plot the graph of historical volatility and implied volatility v/s index and store it in dataset specific folder under output 
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function plotTrade in module dataHandler:

plotTrade(id, indexes, result)
    Plot the graph of trade with Vega * (IV - HV) v/s index and with historical and implied volatility v/s index and store it in dataset specific folder under output 
    
    Parameters :
    id (int) : ID of the position for which trade needs to be plotted
    indexes (list) : list of indices according to the dataset which need to be plotted
    result (string) : 'profit' / 'loss' for determining the color with which trade needs to be plotted
    
    Returns : 
    void

functions.py
-------------------------------------------------------------------------------------------------------------------------
Help on function loadExpiryDates in module functions:

loadExpiryDates()
    Loads the expiry dates for all months from the config file
    
    Parameters :
    (void)
    
    Returns : 
    void

Help on function roundToNearestInt in module functions:

roundToNearestInt(val)
    Rounds off the value to nearest integer value
    
    Parameters :
    val (float) : Value which needs to be rounded off
    
    Returns : 
    int : Value rounded off to nearest integer

Help on function getExpiryDate in module functions:

getExpiryDate(query_date)
    Retrieve the expiry date for the query date
    
    Parameters :
    query_date (datetime object) : Date for which expiry date needs to be returned
    
    Returns : 
    datetime object : Expiry date for the queried date

Help on function convertMinutesToDays in module functions:

convertMinutesToDays(query_time)
    Returns the time remaining(in days) for the current day to end in decimal
    
    Parameters :
    query_time (datetime object) : Time for which the time remaining until dayend(in days) needs to be calculated in decimal
    
    Returns : 
    float : Time remaining until the day end (in days according to current time)

Help on function discountByRate in module functions:

discountByRate(future_price, rate, curr_date)
    Returns the discounted price according to provided rate and time, used to calculate stock price from future price
    
    Parameters :
    future_price (float) : Price of future currently
    rate (float) : Risk free rate in market in decimal (0, 1)
    curr_date (datetime object) : Current date to calculate time remaing for which disount is to be done
    
    Returns : 
    float : Future price discounted on given rate for given time till expiry

Help on function convertTimeToIST in module functions:

convertTimeToIST(date_obj)
    Function to convert the given time to IST
    
    Parameters :
    date_obj (datetime object) : The datetime object which needs to be convereted to IST
    
    Returns : 
    datetime object : The input converted to IST

gamma.py
-------------------------------------------------------------------------------------------------------------------------
Help on class GammaScalping in module gamma:

class GammaScalping(builtins.object)
 |  Class definition to construct and monitor gamma scalping object
 |  
 |  Parameters :
 |  symbol (string) : The symbol of the asset which is under consideration
 |  call_strike (float) : Strike price of call option bought / sold
 |  put_strike (float) : Strike price of put option bought / sold
 |  call_expiry (float) : Time till expiration of call option expressed in years
 |  put_expiry (float) : Time till expiration of put option expressed in years
 |  num_contracts_call (int) : number of contracts of call bought / sold
 |  num_contracts_put (int) : number of contracts of put bought / sold
 |  contr_size (int) : Contract size of the asset
 |  risk_free_rate (float) : Risk free rate in market in decimal (0, 1)
 |  curr_date (datetime) : Date on which object was initialised
 |  gamma_position (string) : 'LONG' / 'SHORT' Position which is taken
 |  init_idx (int) : Index according to the database on which object was initialised
 |  iv_tol (float) : Maximum tolerable difference between the actual option premium and premium using calculated volatility
 |  pos_id (int) : Position ID for the gamma_scalp object (id of position under which this object was initialised)
 |  
 |  option_value_traded (float) : Total amount of option value traded for calculation of transaction cost
 |  future_valur_traded (float) : Total amount of future value traded for calculation of transaction cost
 |  
 |  Methods defined here:
 |  
 |  __init__(self, symbol, call_strike, put_strike, call_expiry, put_expiry, num_contracts_call, num_contracts_put, contr_size, risk_free_rate, curr_date, gamma_position, init_idx, iv_tol, pos_id)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  calcDelta(self, idx)
 |      Used to calculate delta for the position (for this particular gamma_scalp object)
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset for which delta needs to be calculated
 |      
 |      Returns :
 |      float : Delta value for the position
 |  
 |  closePosition(self, idx)
 |      Used for closing the position
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset for where position needs to be closed
 |      
 |      Returns :
 |      float : Total profit / loss after closing the position
 |  
 |  deltaHedge(self, idx)
 |      Used to calculate delta, check if delta is away from zero and perform buying and selling to bring delta close to zero
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset for which delta hedging needs to be done
 |      
 |      Returns :
 |      float : Total profit or loss if the position is closed at given index
 |  
 |  getOptionsCurrentCost(self, idx, type_of_price)
 |      Extraction of premium for the call and put option from the dataset 
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset for which the call and put premium needs to be evaluated
 |      type_of_price (string) : 'bid', 'ask' or 'avg' according to which type of price is required
 |      
 |      Returns :
 |      float : Option premium sum for all calls and puts in hand
 |  
 |  optionBalanceHelperFunction(self, idx, signal)
 |      Function to find option balance at given index, helps to find out the profit / loss if the option position is closed at current index
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset where the balance of the options need to be evaluated
 |      signal (string) : 'ENTER' / 'EXIT' depending on for whether the balance needs to be calculated for entry into position or exit from the position
 |      
 |      Returns : 
 |      float : Balance of options in hand for the specified signal
 |  
 |  updateTimeTillExpiration(self, idx)
 |      Used to update time till expitation for the call option and put option expiry, which is used later for delta calculation
 |      
 |      Parameters :
 |      idx (int) : Index according to the dataset which needs to be accounted for time update
 |      
 |      Returns :
 |      void
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)

main.py
-------------------------------------------------------------------------------------------------------------------------
Controls the overall flow of the program

position.py
-------------------------------------------------------------------------------------------------------------------------
Help on class Position in module position:

class Position(builtins.object)
 |  Class definition to construct and monitor position that is taken at any instant
 |  
 |  Parameters :
 |  id (int) : The id for this position object so that it can be identified uniquely
 |  gamma_object (Gamma Scalping object) : The underlying gamma scalping object for the position
 |  status (string) : 'LONG' / 'SHORT' depending on the position which is taken
 |  start_iv (float) : Implied Volatility value at start of the position
 |  start_hv (float) : Historical Volatility value at start of the position
 |  break_off_vega (float) : Value below / above which the position needs to be exited
 |  max_tolerable_vega (float) : Max value of parameter Vega * (IV - HV) that can be tolerated if the movements of opposite of what we expect
 |  idx (int) : Index according to the dataset where the position has benn taken
 |  
 |  Methods defined here:
 |  
 |  __init__(self, id, gamma_object, status, start_iv, start_hv, break_off_vega, max_tolerable_vega, idx)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  closePosition(self, i, impl_volatility, hist_volatility, close_signal)
 |      Function for closing the position by calling close for the gamma scalping object of the position
 |      
 |      Parameters :
 |      i (int) : Index according to the dataset where evaluation needs to be done
 |      impl_volatility (float) : Implied Volatility at the index where evaluation needs to be done
 |      hist_volatility (float) : Historical Volatilitiy at the index where evaluation needs to be done
 |      close_signal (string) : The reason due to which this position is being closed
 |      
 |      Returns :
 |      void
 |  
 |  evaluate(self, impl_volatility, hist_volatility, vega, i)
 |      Function of evaluate the gamma scalping object of the position at new index, check if hedging is to be performed or the position needs to be closed according to the parameter value
 |      
 |      Parameters :
 |      impl_volatility (float) : Implied Volatility at the index where evaluation needs to be done
 |      hist_volatility (float) : Historical Volatilitiy at the index where evaluation needs to be done
 |      vega (float) : Vega value at the index where evaluation needs to be done
 |      i (int) : Index according to the dataset where evaluation needs to be done    
 |      
 |      Returns :
 |      void
 |  
 |  plot(self)
 |      Function to plot the trade points for the position
 |      
 |      Parameters :
 |      (void)
 |      
 |      Returns :
 |      void
 |  
 |  unchartered_territory(self, impl_volatility, hist_volatility, vega, i)
 |      Function to check if the deviation from expected move if too large and exit the position accordingly
 |      
 |      Parameters :
 |      impl_volatility (float) : Implied Volatility at the index where checking needs to be done
 |      hist_volatility (float) : Historical Volatilitiy at the index where checking needs to be done
 |      vega (float) : Vega value at the index where checking needs to be done
 |      i (int) : Index according to the dataset where checking needs to be done
 |      
 |      Returns :
 |      boolean : True if the deviation is too much, False if not
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)

requestHandler.py
-------------------------------------------------------------------------------------------------------------------------
Help on function openOutputFile in module requestHandler:

openOutputFile(folder_name)
    Function to initiate file objects for writing trade data and summary data
    
    Parameters : 
    folder_name (string) : name of folder under which the summary file, trade data file and plots needs to be placed
    
    Returns : 
    void

Help on function closeOutputFile in module requestHandler:

closeOutputFile()
    Function to close the files opened for writing the trade and summary data
    
    Parameters : 
    (void)
    
    Returns : 
    void

Help on function sellRequest in module requestHandler:

sellRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current)
    Function to sell the specified quantity of asset and return the balance change of futures, also calculates the total PnL if the position is closed at current index
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    action (string) : Action to be performed ('EXIT' / 'HEDGE')
    quantity (int) : Quantity of the asset to be sold
    idx (int) : Index of the dataset file(row number) for which request needs to be evaluated
    total_futures (int) : Amount of futures currently in hand
    future_balance (float) : Net balance of futures currently in hand
    option_balance_init (float) : Option net balance when the position was initialised
    option_balance_current (float) : Option net balance at current index
    
    Returns : 
    if action == 'HEDGE'
    float : Balance change in futures by selling specified quantity at current market price (at current index)
    float : Total PnL if this position was closed at current index
    
    if action == 'EXIT'
    float : Total PnL after closing this position at current index
    float : Balance change in futures by buying specified quantity at current market price (at current index)

Help on function buyRequest in module requestHandler:

buyRequest(pos_id, action, quantity, idx, delta, total_futures, future_balance, option_balance_init, option_balance_current)
    Function to buy the specified quantity of asset and return the balance change of futures, also calculates the total PnL if the position is closed at current index
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    action (string) : Action to be performed ('EXIT' / 'HEDGE')
    quantity (int) : Quantity of the asset to be bought
    idx (int) : Index of the dataset file(row number) for which request needs to be evaluated
    total_futures (int) : Amount of futures currently in hand
    future_balance (float) : Net balance of futures currently in hand
    option_balance_init (float) : Option net balance when the position was initialised
    option_balance_current (float) : Option net balance at current index
    
    Returns : 
    if action == 'HEDGE'
    float : Balance change in futures by buying specified quantity at current market price (at current index)
    float : Total PnL if this position was closed at current index
    
    if action == 'EXIT'
    float : Total PnL after closing this position at current index
    float : Balance change in futures by buying specified quantity at current market price (at current index)

Help on function writePositionDataToTradeFile in module requestHandler:

writePositionDataToTradeFile(idx, pos_id, status)
    Function to write position opening and closing data to trade file
    
    Parameters : 
    idx (int) : Current index according to dataset for which the data is to be written
    pos_id (int) : Position ID for the gamma scalping object
    status (string) : 'LONG START / SHORT START / LONG EXIT / SHORT EXIT' depending on the position taken / closed
    
    Returns : 
    void

Help on function writeToSummaryFile in module requestHandler:

writeToSummaryFile(pos_id, start_timestamp, end_timestamp, position_taken, entry_iv, entry_hv, exit_iv, exit_hv, total_pnl, close_signal)
    Function to write the summary for the position, the entry timestamp, exit timestamp, entry IV, exit IV, entry HV, exit HV, total PnL etc.
    
    Parameters : 
    pos_id (int) : Position ID for the gamma scalping object
    start_timestamp (string) : Start timestamp for the position
    end_timestamp (string) : End timestamp for the position
    entry_iv (float) : Implied Volatility when the position was initiated
    entry_hv (float) : Historical Volatility when the position was initiated
    exit_iv (float) : Implied Volatility when the postition was closed
    exit_hv (float) : Historical Volatility when the position was closed
    total_pnl (float) : Total profit / loss encountered from this position
    close_signal (string) : Reason for which the position was closed
    
    Returns : 
    void

