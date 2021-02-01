import click
import pandas as pd
import pandas_datareader as web
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

@click.command()
@click.option('-r', '--risk-free-rate', default=0.02)
@click.option('-s', '--start', default='2011-01-01')
@click.option('-S', '--span', default=252*5)
@click.option('-v', '--verbose', count=True)
@click.argument('tickers', nargs=-1, required=True)
def cli(risk_free_rate, start, span, verbose, tickers):
    # Read in price data
    thelen = len(tickers)
    price_data = []
    successful_tickers = []
    for ticker in range(thelen):
        click.echo(tickers[ticker])
        try:
            prices = web.DataReader(tickers[ticker], start=start, data_source='yahoo')
            if verbose >= 1:
                click.echo(tickers[ticker] + ':')
                click.echo(prices)
            price_data.append(prices.assign(ticker=ticker)[['Adj Close']])
            successful_tickers.append(tickers[ticker])
        except:
            pass
    
    df = pd.concat(price_data, axis=1)
    df.columns=successful_tickers
    df.head()

    #Checking if any NaN values in the data
    nullin_df = pd.DataFrame(df,columns=tickers)
    print(nullin_df.isnull().sum())

    # Calculate expected returns and sample covariance
    mu = expected_returns.ema_historical_return(df, span=span)
    S = risk_models.sample_cov(df)

    # Optimise for maximal Sharpe ratio
    ef = EfficientFrontier(mu, S) #weight bounds in negative allows shorting of stocks
    raw_weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
    cleaned_weights = ef.clean_weights()
    click.echo(cleaned_weights)
    ef.portfolio_performance(verbose=True)