import numpy as np
import scipy.stats as si

# S : spot price
# K : strike price
# T : time to expiry (in years)
# r : risk free interest rate (in decimal)
# sigma : volatility (in decimal)
# days : number of trading days per year

def getOptionPremiumBS(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option == 'call':
        result = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    if option == 'put':
        result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return result

def getImpliedVolatilityBS(C, S, K, T, r, idx, precision):
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
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = si.norm.cdf(d1, 0.0, 1.0)
    if option == 'put':
        result = -si.norm.cdf(-d1, 0.0, 1.0)
    return result

def getGammaBS(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
    return result

def getThetaBS(S, K, T, r, sigma, option, days):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option == 'call':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    if option == 'put':
        result = -(S * sigma * si.norm.pdf(d1, 0.0, 1.0)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    return result / days

def getVegaBS(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    result = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
    return result
