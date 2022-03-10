from importlib import resources
import pickle, jmespath

file = 'bounties_27564.pkl'
with resources.open_binary('data', file) as f:
    bounties = pickle.load(f)

query = '[*][0].pk'
print(jmespath.search(query, bounties))
print(len(bounties))

