import sys, pickle, logging, datetime

from helpers import get_path, config
from github2 import GithubGetter, GithubLoader

logfile = '/Users/kyunghee/Documents/Github/gitcoin/var/tmp/' + datetime.datetime.now().strftime('github_api_%Y-%m-%dT%H-%M-%S.log')
logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

token = config('GITHUB')['token']

if __name__=="__main__":
    with get_path('var.cache', 'bounty.pkl').open('rb') as f:
        bounties = pickle.load(f)
    
    file = 'data/github5.pkl'
    # interval = 100

    start_index = GithubLoader.restore(file)
    GithubGetter.authenticate(token)

    for i, bounty in enumerate(bounties[start_index:]):
        pk = int(bounty['pk'])
        config = {
            "pk": pk,
            "github_issue_number": int(bounty['github_issue_number']),
            "github_org_name": bounty['github_org_name'],
            "github_repo_name": bounty['github_repo_name'],
            "bounty_owner_github_username": bounty['bounty_owner_github_username'],
        }
        if not GithubLoader.is_loaded(pk):
            try:
                response = GithubGetter(**config)
                GithubLoader(response)
            except:
                GithubLoader.to_pkl(file)
                sys.exit("Exit program ...")

    GithubLoader.to_pkl(file)