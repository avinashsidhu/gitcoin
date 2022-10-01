from attrs import define, field
import datetime
from .user2 import User
from helpers import to_date, to_float, ToDictMixin

@define(slots=False)
class Event(ToDictMixin):
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

@define(slots=False)
class Activity(Event):
    activity_type: str

    @classmethod    
    def from_dict(cls, event):
        return cls(event['pk'], event['event_pk'], event['created'], event['handle'], event['activity_type'])

class Interest(Event): pass

@define(slots=False)
class Fulfillment(Event):
    token_name: str
    payout_status: str
    payout_amount: float = field(converter=to_float)
    hoursworked: float = field(converter=to_float)
    address: str

    @classmethod
    def from_dict(cls, event):
        return cls(event['pk'], event['event_pk'], event['created'], event['handle'], event['token_name'], event['payout_status'], event['payout_amount'], event['hoursworked'], event['fulfiller_address'])
