#%%
# TODO
# review all the if statements
# eth wallet: total asset, total transaction, num of tokens, nft holder?, erc-20 tokens?
from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd
from user import UserTally, User, OwnerTally, Owner, comp_type
from event import Activity, Fulfillment, Interest
from helpers import convert_to_float, convert_to_date, convert_type
from githubattr import GithubRepo, GithubIssue, GithubUser

_vars = [
        'pk', 'org_name', 'project_type', 'experience_level', 'permission_type',
        'created', 'fulfillment_started_on', 'fulfillment_submitted_on', 'fulfillment_accepted_on',
        'token_name', 'value_in_usdt', 'comp_type',
        'github_comments', 'num_interests', 'num_fulfillments',
        'submitted', 'accepted', 'cancelled', 'elapased_days_from_created', 'elapased_days_from_start', 
        'totalhours', 'totalsubs', 'totalfulfillments', 'totalearned', 'token_ratio', 'totalownedbounties',
        'url', 'bounty_owner_github_username', 'github_org_name', 'github_issue_number', 'github_url', 'is_open', 'status', 'network',
    ]

def get_eventclass(event_type):
    factories = {
        'activity': Activity,
        'fulfillment': Fulfillment,
        'interest': Interest
    }
    try:
        return factories[event_type]
    except KeyError:
        raise KeyError(f'Invalid event type: {event_type}')

@dataclass
class Bounty:
    pk: int
    url: str
    paid: List[str]
    network: str
    title: str
    status: str
    is_open: bool
    keywords: str
    project_type: str
    experience_level: str
    permission_type: str
    github_url: str
    github_issue_number: int
    github_repo_name: str
    github_comments: str
    github_issue_state: str
    token_name: str
    value_in_usdt: str
    value_true: str
    value_in_eth: str
    value_in_token: str
    created: str
    expires_date: str
    created_on: str
    modified_on: str
    cancelled_on: str
    fulfillment_started_on: str
    fulfillment_submitted_on: str
    fulfillment_accepted_on: str
    org_name: str
    github_org_name: str
    bounty_owner_name: str
    bounty_owner_email: str
    bounty_owner_address: str
    bounty_owner_github_username: str
    fulfillment: List[dict]
    interest: List[dict]
    activity: List[dict]

    def __post_init__(self):
        _datevars = ['created', 'expires_date', 'created_on', 'modified_on', 'cancelled_on', 'fulfillment_started_on', 'fulfillment_submitted_on', 'fulfillment_accepted_on']
        _numvars = ['value_in_usdt', 'value_true', 'value_in_eth', 'value_in_token']
        convert_type(self, _datevars, convert_to_date)
        convert_type(self, _numvars, convert_to_float)
        
        self.fulfillmenet = self._update('fulfillment')
        self.interest = self._update('interest')
        self.activity = self._update('activity')

        if self.org_name:
            self.owner = Owner(self.org_name)
            self.owner._update(self)
        
        # search by pk
        # self.githubuser = GithubUser(self.github_org_name)    
        # self.repo = GithubRepo(self.githubuser, self.github_repo_name, self.created)
        # self.issue = GithubIssue(self.repo.repo, self.github_issue_number)


    def _update(self, event_type):
        _obj_lst = []
        events = getattr(self, event_type)
        eventclass = get_eventclass(event_type)
        for event in events:
            event['pk'] = self.pk
            event_obj = eventclass(**event)
            event_obj.update()
            _obj_lst.append(event_obj)
        return _obj_lst
    
    def get_owner_attr(self, method):
        if self.org_name:        
            return getattr(OwnerTally(Owner(self.org_name), self.created), method)

    def get_user_attr(self, method):
        if self.interest:
            attrs = [getattr(UserTally(User(applicant.handle), self.created), method) for applicant in self.interest]
            return np.mean(attrs)
    
    def _is_valid(self): 
        if self.network=="mainnet":
            return True
        '''
        until 12/31/2021,
        remove open; done or cancelled
        '''
        pass
    
    def to_dict(self, varlist):
        # unpack objects
        dict = {}
        for var in varlist:
            dict[var] = getattr(self, var)
        return dict

    @property
    def cancelled(self):
        '''or canceled_on is None'''
        return self.status=='cancelled'
    @property
    def submitted(self):
        return self.fulfillment_submitted_on is not None
    @property
    def accepted(self):
        return self.fulfillment_accepted_on is not None
    @property
    def num_interests(self):
        return len(self.interest)
    @property
    def num_fulfillments(self):
        return len(self.fulfillment)
    @property
    def elapased_days_from_created(self):
        if self.accepted:
            try:
                return (self.fulfillment_submitted_on - self.created).days
            except TypeError:
                return None
    @property
    def elapased_days_from_start(self):
        if self.accepted:
            try:
                return (self.fulfillment_submitted_on - self.fulfillment_started_on).days
            except TypeError:
                return None
    @property
    def delayed_days(self):
        '''often not valid due to inaccurate expires_date'''
        if self.accepted:
            try:
                return (self.fulfillment_submitted_on - self.expires_date).days
            except TypeError:
                return None
    @property
    def comp_type(self):
        return comp_type(self.token_name)
    
    @property
    def totalhours(self):
        return self.get_user_attr('totalhours')
    @property
    def totalsubs(self):
        return self.get_user_attr('totalsubs')
    @property
    def totalfulfillments(self):
        return self.get_user_attr('totalfulfillments')
    @property
    def totalearned(self):
        return self.get_user_attr('totalearned')
    @property
    def token_ratio(self):
        return self.get_user_attr('token_ratio')
    @property
    def totalownedbounties(self):
        return self.get_owner_attr('totalownedbounties')

#%%
if __name__=='__main__':
    from helpers import get_path
    import jmespath, json
    from query import query
    
    # Load data
    file = 'data_toy.json'
    with get_path('data', file).open('r') as f:
        data_json = json.load(f)
    data = jmespath.search(query, data_json)
    bounties = [Bounty(**record) for record in data]
#%%
    bounties_dict = [bounty.to_dict(_vars) for bounty in bounties]
#%% 
    df = pd.DataFrame(bounties_dict).set_index('pk')
    df
    # df.to_csv('var/cache/bounty.csv')
    # df.to_pickle('var/cache/bounty.pkl')
    # df.to_stata('var/cache/bounty.dta')