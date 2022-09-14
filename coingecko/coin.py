#%%
from datetime import datetime, timezone, timedelta
import pandas as pd
from attrs import define
from helpers import ToDictMixin
from scipy import stats

@define(slots=False)
class CoinWrapper(ToDictMixin):
    before_listed: bool
    volume: float
    price: float
    avg_price: float
    avg_return: float
    std_return: float
    kurt_return: float
    skew_return: float
    momentum: float
    roc: float
    prob_not_zero: float
    
    @classmethod
    def setup(cls, symbol, date):
        coin = Coin(symbol)
        coin.read_data()
        return cls(
            coin.before_listed(date),
            coin.get_volume(date),
            coin.get_price(date),
            coin.avg_price(date),
            coin.avg_return(date),
            coin.std_return(date),
            coin.kurt_return(date),
            coin.skew_return(date),
            coin.momentum(date),
            coin.roc(date),
            coin.prob_not_zero(date)
        )

class Coin:
    '''
    Coin price stats from historical data
    '''
    def __init__(self, symbol) -> None:
        self.symbol = symbol

    @property
    def data_path(self) -> str:
        return f'data/coins/{self.symbol}-usd.csv'

    def read_data(self):
        df = pd.read_csv(self.data_path)
        df['snapped_at'] = pd.to_datetime(df['snapped_at'], utc=True).dt.date
        df['daily_return'] = df.price.pct_change()
        self.df = df

    def before_listed(self, date):
        return self.df.snapped_at.iloc[0]>date

    def get_volume(self, date):
        try:
            return self.df[self.df.snapped_at==date]['total_volume'].iloc[0]
        except IndexError: # no matching date
            return None        

    def get_price(self, date):
        # UPDATE: date type check
        try:
            return self.df[self.df.snapped_at==date]['price'].iloc[0]
        except IndexError: # no matching date
            return None
    
    def _window(self, var, date, period=30):
        start = date - timedelta(period)
        # error?
        return self.df[(self.df.snapped_at>=start)&(self.df.snapped_at<date)][var]

    def avg_price(self, date, period=30):
        prices = self._window('price', date, period)
        return prices.mean()
    
    def avg_return(self, date, period=30):
        returns = self._window('daily_return', date, period)
        return returns.mean()
    
    def std_return(self, date, period=30): 
        returns = self._window('daily_return', date, period)
        return returns.std()
    
    def kurt_return(self, date, period=30): 
        returns = self._window('daily_return', date, period)
        return returns.kurtosis()
    
    def skew_return(self, date, period=30): 
        returns = self._window('daily_return', date, period)
        return returns.skew()

    def momentum(self, date, period=10):
        '''source: https://tradesanta.com/blog/momentum-indicators-and-how-to-use-them'''
        price = self.get_price(date)
        start = date - timedelta(period)
        price_period_ago = self.get_price(start)
        
        if price and price_period_ago:
            return price - price_period_ago
    
    def roc(self, date, period=10):
        '''Rate of Change'''
        start = date - timedelta(period)
        price_period_ago = self.get_price(start)
        momentum = self.momentum(date, period)
        
        if price_period_ago and momentum:
            return momentum/price_period_ago
    
    def prob_not_zero(self, date, period=30):
        returns = self._window('daily_return', date, period)
        if not returns.empty:
            return stats.ttest_1samp(a=returns, popmean=0).pvalue

#%%
if __name__=="__main__":
    symbol = 'bitcoin' # change to symbol
    date = datetime(2020,1,1, tzinfo=timezone.utc)
    stats = CoinWrapper.setup(symbol, date)
    print(stats)
