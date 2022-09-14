import jmespath, json
from helpers import get_path
from etc.query import query
from tqdm import tqdm
from coingecko import CoinGeckoScraper

file = 'data.json'
with get_path('data', file).open('r') as f:
    data_json = json.load(f)
data2 = jmespath.search(query, data_json)

token_set = set([record['token_name'] for record in data2 if record['token_name']])

for symbol in tqdm(token_set, desc='Fetching...'):
    cg = CoinGeckoScraper(symbol)
    cg.get_price_chart()