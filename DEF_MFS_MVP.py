from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

class stocks:

    def download(self, x):
        for ticker in x:
            data = yf.download(ticker, group_by="Ticker", start="2021-01-01", end="2021-12-31")
            data['ticker'] = ticker  # add this column because the dataframe doesn't contain a column with the ticker
            data.to_csv(f'ticker_{ticker}.csv')  # ticker_F.csv for example

tick = ['F',"TSLA"]
stock = stocks()
stock.download(tick)