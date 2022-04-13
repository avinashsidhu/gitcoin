#%%
from helpers import get_path
import jmespath, json
from query import query
from bounty import Bounty, _vars
import pandas as pd

# Load data
file = 'data.json'
with get_path('data', file).open('r') as f:
    data_json = json.load(f)
data = jmespath.search(query, data_json)
bounties = [Bounty(**record) for record in data]
#%%
bounties_dict = [bounty.to_dict(_vars) for bounty in bounties]
#%% 
df = pd.DataFrame(bounties_dict).set_index('pk')
df.experience_level.value_counts()
#%%
df.to_csv('var/cache/bounty.csv')
df.to_pickle('var/cache/bounty.pkl')
df.to_stata('var/cache/bounty.dta', version=118)