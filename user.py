# __call__ to validate User class?
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

#mixin?

class User:
    _loaded = {}

    def __new__(cls, handle):
        if handle:
            user = cls._loaded.get(handle)
        else:
            return None
        if user is not None:
            return user        
        user = super().__new__(cls)
        user.handle = handle
        user.activity = []
        user.interest = []
        user.fulfillment = []
        user.bounty = []  # for Owner
        cls._loaded[handle] = user
        return user
    
    def __repr__(self):
        return f'(User {self.handle}: activity={self.tally("activity")}, interest={self.tally("interest")}, fulfillment={self.tally("fulfillment")})'
    
    def _update(self, attr):
        called_from = type(attr).__name__.lower()
        getattr(self, called_from).append(attr)

class Owner(User):
    def totalownedbounties(self, date):
        bounties = [bounty for bounty in self.bounty if bounty.created<date]
        return len(bounties)

class UserTally:
    def __init__(self, user: User, date) -> None:
        self.date = date
        # use convert_type?
        self.fulfillment = filter(user.fulfillment, date)
        self.activity = filter(user.activity, date)
        self.interest = filter(user.interest, date)
        self.bounty = filter(user.bounty, date)
    
    @property
    def totalhours(self):
        hours = [work.hoursworked for work in self.fulfillment if work.hoursworked is not None]
        return sum(hours)
    @property
    def totalearned(self):
        amounts = [work.payout_amount for work in self.fulfillment if work.payout_amount is not None]
        return sum(amounts)    
    @property        
    def totalbounties(self):
        pass
    @property        
    def totalsubs(self):
        subs = [work for work in self.activity if work.activity_type=='work_submitted']
        return len(subs)
    @property    
    def totalfulfillments(self):
        acceptedsubs = [work for work in self.fulfillment]
        return len(acceptedsubs)
    @property        
    def token_ratio(self):
        tokens = [work.token_name for work in self.fulfillment if comp_type(work.token_name)=='token']
        try:
            return len(tokens)/self.totalfulfillments
        except ZeroDivisionError:
            return 0 # is this right?

class OwnerTally(UserTally):
    @property
    def totalownedbounties(self):
        bounties = [bounty for bounty in self.bounty]
        return len(bounties)