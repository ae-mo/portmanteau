import click
from pandas_datareader import data as pdr
import datetime
import requests_cache
import yfinance as yf
import pandas as pd
from click.utils import echo
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
@click.option('-f', '--files', type=click.File('r'), multiple=True)
@click.argument('tickers', nargs=-1)
def cli(risk_free_rate, start, span, verbose, files, tickers):

    # Override pandas_datareader
    yf.pdr_override()

    # Check files first
    try:
      for file in files:
        lines = file.readlines()
        lines = [line.strip() for line in lines if not line.strip().startswith("#")]
        tickers = tickers + tuple(lines)
    except:
      pass

    # Read in price data
    thelen = len(tickers)
    price_data = []
    successful_tickers = []

    # Setup cache
    DEFAULT_HEADERS = DEFAULT_HEADERS = {
        "Connection": "keep-alive",
        "Expires": str(-1),
        "Upgrade-Insecure-Requests": str(1),
        # Google Chrome:
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
    }
    expire_after = datetime.timedelta(days=3)
    session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
    session.headers = DEFAULT_HEADERS

    for ticker in range(thelen):
        click.echo(tickers[ticker])
        try:
          prices = pdr.get_data_yahoo(tickers[ticker], start=start, session=session)
          price_data.append(prices.assign(ticker=ticker)[['Adj Close']])
          successful_tickers.append(tickers[ticker])
        except:
          click.echo(tickers[ticker] + ': error encountered, skipping')

    if verbose >= 1:
      click.echo(price_data)

    df = pd.concat(price_data, axis=1)

    if verbose >= 1:
      click.echo(df)

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
    click.echo([ (w, cleaned_weights[w]) for w in cleaned_weights if cleaned_weights[w] > 0])
    ef.portfolio_performance(verbose=True)