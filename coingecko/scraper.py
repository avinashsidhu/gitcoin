from functools import cached_property
from requests_html import HTMLSession
from pathlib import Path
from pycoingecko import CoinGeckoAPI
import jmespath

class CoinGecko:
    coin_list = CoinGeckoAPI().get_coins_list()

    def get_symbol(self, id):  
        query = f"[?id=='{id.lower()}']"
        results = jmespath.search(query, self.coin_list)
        try: 
            return results[0]['symbol']
        except IndexError:
            return None

    def get_id(self, symbol):
        query = f"[?symbol=='{symbol.lower()}']"
        results = jmespath.search(query, self.coin_list)
        try: 
            return results[0]['id']
        except IndexError:
            return None

class CoinGeckoScraper:
    baseurl = 'https://www.coingecko.com'
    charturl = '/en/coins/%s/historical_data/usd#panel'
    dir = 'data/coins/'
    session = HTMLSession()

    def __init__(self, coin_symbol) -> None:
        self.coin_symbol = coin_symbol

    @cached_property
    def coin_id(self):
        return CoinGecko().get_id(self.coin_symbol)
    @property
    def coin_url(self):
        return self.baseurl + self.charturl % self.coin_id
    @cached_property
    def chart_url(self):
        if self.coin_id:
            r = self.session.get(self.coin_url)
            try:
                csvurl = r.html.find('a[href$=".csv"]')[0].attrs['href']
                return self.baseurl + csvurl
            except IndexError:
                return None
        else:
            return None
    @property
    def file(self):
        return f'{self.dir}/{self.coin_symbol}-{Path(self.chart_url).name}'
    def get_price_chart(self):
        if self.chart_url:
            r = self.session.get(self.chart_url, allow_redirects=True)
            open(self.file, 'wb').write(r.content)
        else:
            print('No file')