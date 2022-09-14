#%%
import jmespath, json
from tqdm import tqdm
import pandas as pd

from gitcoin import Bounty
from github2 import GithubWrapper
from etc.query import query
from attrs import asdict

from helpers import get_path

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
bounties_dict = [bounty.to_dict() for bounty in bounties]
# bounties_dict = [asdict(bounty) for bounty in bounties]
# with get_path('var.cache', 'bounty.pkl').open('wb') as f:
#     pickle.dump(bounties_dict, f)

df = pd.json_normalize(bounties_dict).set_index('pk')
df
#%%
df.to_csv('var/cache/bounty2.csv')
df.to_stata('var/cache/bounty2.dta', version=118)