import requests
from helpers import get_path
import pickle
from tqdm import tqdm

def save(pk, responses):
    file = f'bounties_{pk}.pkl'
    path = get_path('data', file)
    with path.open('wb') as f:
        pickle.dump(responses, f)

url = 'https://gitcoin.co/api/v0.1/bounties/'
pk_lst = range(22563, -1, -1) # start: 28563
cut = 1000

responses=[]
for i, pk in enumerate(tqdm(pk_lst, desc='Fetching: ')):
    params = {'pk': pk}
    response = requests.get(url, params).json()
    if response: 
        responses.append(response)
    if ((i+1)%cut)==0:
        save(pk, responses)
        # print(f'File saved [{i+1}/{len(pk_lst)}]')
        responses=[]

save(pk, responses)

print(f'{len(responses)} bounties fetched')

