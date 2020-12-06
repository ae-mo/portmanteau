import click
import pandas as pd
import pandas_datareader as web
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

@click.command()
def cli():
    # Read in price data
    tickers = ['BSX','AES','BRK-B','SEE','QQQ','SPY']
    thelen = len(tickers)
    price_data = []
    for ticker in range(thelen):
        prices = web.DataReader(tickers[ticker], start='2015-01-01', end = '2020-06-06', data_source='yahoo')
        price_data.append(prices.assign(ticker=ticker)[['Adj Close']])
    
    df = pd.concat(price_data, axis=1)
    df.columns=tickers
    df.head()

    #Checking if any NaN values in the data
    nullin_df = pd.DataFrame(df,columns=tickers)
    print(nullin_df.isnull().sum())

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    # Optimise for maximal Sharpe ratio
    ef = EfficientFrontier(mu, S, weight_bounds=(-1,1)) #weight bounds in negative allows shorting of stocks
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    click.echo(cleaned_weights)
    ef.portfolio_performance(verbose=True)