from user import User
from helpers import convert_to_float, convert_to_date, convert_type
from dateutil import parser

class Event:
    def __init__(self, pk, event_pk, created, handle, **_ignored) -> None:
        self.pk = pk
        self.event_pk = event_pk
        self.created = created
        convert_type(self, ['created'], convert_to_date)
        self.handle = handle
    
    def update(self):
        if self.handle:
            user = User(self.handle)
            user._update(self)
    
class Activity(Event):
    def __init__(self, pk, event_pk, created, handle, activity_type, **_ignored) -> None:
        super().__init__(pk, event_pk, created, handle)
        self.activity_type = activity_type
    def __repr__(self):
        return f'User {self.handle} {self.activity_type} for bounty {self.event_pk} at {self.created}'

class Interest(Event):
    def __repr__(self):
        return f'User {self.handle} shown interest for bounty {self.event_pk} at {self.created}'

class Fulfillment(Event):
    def __init__(self, pk, event_pk, created, handle, tenant, token_name, accepted_on, accepted, payout_amount, payout_status, fulfiller_address, hoursworked, **_ignored) -> None:
        super().__init__(pk, event_pk, created, handle, **_ignored)
        self.token_name = token_name
        self.payout_status = payout_status
        self.payout_amount = payout_amount
        self.hoursworked = hoursworked

        _numvars = ['payout_amount', 'hoursworked']
        convert_type(self, _numvars, convert_to_float)
    def __repr__(self):
        return f'User {self.handle} {self.payout_amount} {self.token_name} paid for bounty {self.event_pk} at {self.created}'