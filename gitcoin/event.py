from attrs import define, field
import datetime
from .user2 import User
from helpers import to_date, to_float

@define
class Event:
    pk: int
    event_pk: int
    created: datetime = field(converter=to_date)
    handle: str

    @classmethod    
    def from_dict(cls, event):
        return cls(event['pk'], event['event_pk'], event['created'], event['handle'])
    def update(self):
        if self.handle:
            user = User.load(self.handle)
            user._update(self)

@define
class Activity(Event):
    activity_type: str

    @classmethod    
    def from_dict(cls, event):
        return cls(event['pk'], event['event_pk'], event['created'], event['handle'], event['activity_type'])

class Interest(Event): pass

@define
class Fulfillment(Event):
    token_name: str
    payout_status: str
    payout_amount: float = field(converter=to_float)
    hoursworked: float = field(converter=to_float)

    @classmethod
    def from_dict(cls, event):
        return cls(event['pk'], event['event_pk'], event['created'], event['handle'], event['token_name'], event['payout_status'], event['payout_amount'], event['hoursworked'])
    # def from_object(cls, pk, event_pk, created, handle, token_name, payout_status, payout_amount, hoursworked, **_ignored):
    #     return cls(pk, event_pk, created, handle, token_name, payout_status, payout_amount, hoursworked)

# class Event:
#     def __init__(self, pk, event_pk, created, handle, **_ignored) -> None:
#         self.pk = pk
#         self.event_pk = event_pk
#         self.created = created
#         convert_type(self, ['created'], convert_to_date)
#         self.handle = handle
    
#     def update(self):
#         if self.handle:
#             user = User(self.handle)
#             user._update(self)
    
# class Activity(Event):
#     def __init__(self, pk, event_pk, created, handle, activity_type, **_ignored) -> None:
#         super().__init__(pk, event_pk, created, handle)
#         self.activity_type = activity_type
#     def __str__(self):
#         return f'User {self.handle} {self.activity_type} for bounty {self.event_pk} at {self.created}'

# class Interest(Event):
#     def __str__(self):
#         return f'User {self.handle} shown interest for bounty {self.event_pk} at {self.created}'

# class Fulfillment(Event):
#     def __init__(self, pk, event_pk, created, handle, tenant, token_name, accepted_on, accepted, payout_amount, payout_status, fulfiller_address, hoursworked, **_ignored) -> None:
#         super().__init__(pk, event_pk, created, handle, **_ignored)
#         self.token_name = token_name
#         self.payout_status = payout_status
#         self.payout_amount = payout_amount
#         self.hoursworked = hoursworked

#         _numvars = ['payout_amount', 'hoursworked']
#         convert_type(self, _numvars, convert_to_float)
#     def __str__(self):
#         return f'User {self.handle} {self.payout_amount} {self.token_name} paid for bounty {self.event_pk} at {self.created}'