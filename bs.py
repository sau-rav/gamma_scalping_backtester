import numpy as np
import scipy.stats as si

def getOptionPremiumBS(S, K, T, r, sigma, option):
    """
    Function to calculate option premium value using Black Scholes model
    
    Parameters : 
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    sigma (float) : Implied Volatility
    option ('call' / 'put') : Type of option for which calculation is to be done

    Returns : 
    float : Premium of the option for given parameter values

    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option == 'call':
        result = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    if option == 'put':
        result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return result


def getImpliedVolatilityBS(C, S, K, T, r, precision):
    """
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
        
    """
    iv_start = 0
    iv_end = 2
    while True:
        mid  = (iv_end + iv_start) / 2
        price_on_mid = getOptionPremiumBS(S, K, T, r, mid, 'call')
        if price_on_mid > C:
            iv_end = mid
        else:
            iv_start = mid
        if np.abs(price_on_mid - C) < precision:
            break
    return mid


def getDeltaBS(S, K, T, r, sigma, option):
    """
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
        
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = si.norm.cdf(d1, 0.0, 1.0)
    if option == 'put':
        result = -si.norm.cdf(-d1, 0.0, 1.0)
    return result


def getGammaBS(S, K, T, r, sigma):
    """
    Function to calculate option's gamma value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility

    Returns : 
    float : Gamma of option for given parameter values 
        
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
    return result


def getThetaBS(S, K, T, r, sigma, option, days):
    """
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
        
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    if option == 'put':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    return result / days


def getVegaBS(S, K, T, r, sigma):
    """
    Function to calculate option's vega value using Black Scholes model
    
    Parameters :
    S (float) : Spot Price (Current price of underlying asset)
    K (float) : Strike Price
    T (float) : Time till expiry of the option (expressed in years)
    r (float) : Risk free rate in decimal (0, 1)
    sigma (float) : Implied Volatility

    Returns : 
    float : Delta of option for given parameter values 
        
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
    return result
