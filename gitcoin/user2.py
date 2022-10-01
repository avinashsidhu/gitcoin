from datetime import datetime
from typing import ClassVar
from attrs import define, field
from helpers import ToDictMixin

def comp_type(token_name):
    coin_category = {
        'fiat': ['USD'],
        'stable': ['USDT', 'USDC', 'UST', 'MIM', 'DAI'],
        'coin': ['BTC', 'ETH', 'SOL', 'ADA', 'LUNA', 'MATIC']
    }
    for k, v in coin_category.items():
        if token_name in v:
            return k
    return 'token'

def filter(lst, date):
    return [i for i in lst if i.created<date]

@define(slots=False)
class User:
    _loaded: ClassVar = {}
    handle: str
    _activity: list = field(factory=list)
    _interest: list = field(factory=list)
    _fulfillment: list = field(factory=list)
    _bounty: list = field(factory=list)

    @classmethod
    def load(cls, handle):
        if handle:
            user = cls._loaded.get(handle)
        else:
            return None
        if user is not None:
            return user        
        
        user = cls(handle)
        cls._loaded[handle] = user
        return user

    def _update(self, attr):
        called_from = '_' + type(attr).__name__.lower()
        getattr(self, called_from).append(attr)
    
    def get_tally(self, date):
        return UserTally.from_object(self, date)
        
@define(slots=False)
class Owner(User): pass

@define(slots=False)
class UserTally(ToDictMixin):
    handle: str
    date: datetime
    _fulfillment: list
    _activity: list
    _interest: list
    _bounty: list
    
    @classmethod
    def from_object(cls, user: User, date):
        return cls(
            user.handle,
            date,
            filter(user._fulfillment, date),
            filter(user._activity, date),
            filter(user._interest, date),
            filter(user._bounty, date)
        )

    @property
    def totalhours(self):
        hours = [work.hoursworked for work in self._fulfillment if work.hoursworked is not None]
        return sum(hours)
    @property
    def totalearned(self):
        amounts = [work.payout_amount for work in self._fulfillment if work.payout_amount is not None]
        return sum(amounts)    
    @property        
    def totalbounties(self):
        pass
    @property        
    def totalsubs(self):
        subs = [work for work in self._activity if work.activity_type=='work_submitted']
        return len(subs)
    @property    
    def totalfulfillments(self):
        acceptedsubs = [work for work in self._fulfillment]
        return len(acceptedsubs)
    @property        
    def token_ratio(self):
        tokens = [work.token_name for work in self._fulfillment if comp_type(work.token_name)=='token']
        try:
            return len(tokens)/self.totalfulfillments
        except ZeroDivisionError:
            return 0 # is this right?

@define(slots=False)
class OwnerTally(UserTally):
    @property
    def totalownedbounties(self):
        bounties = [bounty for bounty in self._bounty]
        return len(bounties)