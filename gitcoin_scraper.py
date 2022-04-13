from proxy import Proxy
from helpers import get_path, config
import random, json
from tqdm import tqdm

def resume(pk_lst, file='data.json'):
    def last_pk(file):
        with get_path('data', file).open('r') as f:
            try: 
                file_data = json.load(f)
                return file_data[-1]['url']['params']['pk']
            except json.decoder.JSONDecodeError: # empty file
                return None
        
    def remove_all_before(item, border):
        try:
            index = item.index(border)+1
            print(f'the border is found at index {index}')
            return item[index:]
        except ValueError:
            print('border not present')
            return item

    last_pk = last_pk(file)
    if last_pk:
        print(f'Resume from last fetched bounty: {last_pk}')
    else:
        print(f'Start from beginning.')
    return remove_all_before(pk_lst, last_pk)

# Set up
config = config()
proxy = Proxy(config)
print(proxy)

# List of PKs to collect
pk_lst = list(range(28563, 0, -1))
random.seed(100)
random.shuffle(pk_lst)

pk_lst = resume(pk_lst)

for pk in tqdm(pk_lst, desc='Fetching: '):
    url = {
        'url' : 'https://gitcoin.co/api/v0.1/bounties/',
        'params' : {'pk': pk}
    }
    proxy.shuffle()
    r = proxy.get(url)

    # export to json
    r.to_json()
    # export to pickle
    r.to_pkl()