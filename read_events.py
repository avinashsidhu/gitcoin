# Read event data for user-level analysis
#%%
import jmespath, json
from tqdm import tqdm
import pandas as pd
import itertools

from gitcoin import Bounty
from github2 import GithubWrapper
from etc.query import query

from helpers import get_path

from gitcoin.user2 import User
from coingecko import CoinWrapper

#%%
# Load data
file = 'data.json'
with get_path('data', file).open('r') as f:
    data_json = json.load(f)

data = jmespath.search(query, data_json)
GithubWrapper.load('github5.pkl')

bounties = []
for record in tqdm(data):
    try:
        bounty = Bounty(**record)
        bounty.update_events()
        bounty.get_github_stats()
        bounty.get_coin_stats()
    except ValueError:
        continue
    bounties.append(bounty)

#%%
# add UserTally and CoinStats to Event

def get_tally(event):
    user = User.load(event.handle)
    if user:
        tally = user.get_tally(event.created).to_dict()
        del tally['handle']
        del tally['date']
        return tally
    else:
        return {}

def get_coin_stats(token, start_date, end_date):
    return {
    'coin_stats_7' : CoinWrapper.setup(token, start_date, period=7).to_dict(),
    'coin_stats_30' : CoinWrapper.setup(token, start_date, period=30).to_dict(),
    'coin_stats_bw' : CoinWrapper.setup(token, start_date, period=[start_date,end_date]).to_dict(),
    }
        
def get_bounty_tally(bounty, event_type):
    token = bounty.token_name
    start_date = bounty.created
    events = getattr(bounty, f'_{event_type}')
    lst = []
    if events:
        for event in events:
            end_date = event.created
            try:
                coin_stats = get_coin_stats(token, start_date, end_date)
            except FileNotFoundError:
                coin_stats = {}
            
            tally = get_tally(event)
            row = {**event.to_dict(), **{'bounty_token': token, 'bounty_created': start_date}, **tally, **coin_stats}
            lst.append(row)
    return lst

event_types = ['fulfillment', 'interest', 'activity']
data_dict = {
    event_type: list(itertools.chain(*[get_bounty_tally(bounty, event_type) for bounty in bounties if bounty.permission_type=='approval' and bounty.project_type=='traditional'])) 
    for event_type in event_types
    }

#%%
for event_type,lst in data_dict.items():
    df = pd.json_normalize(lst).set_index('pk')
    df.to_csv(f'var/cache/{event_type}.csv')
    # df.to_stata(f'var/cache/{event_type}_temp.dta', version=118)
