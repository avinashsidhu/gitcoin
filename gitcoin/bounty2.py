#%%
from typing import Type
from attrs import define, field
import numpy as np
import datetime
from github2.dataclasses import GithubWrapper

from helpers import ToDictMixin, to_date, to_float, to_int
from .user2 import UserTally, User, Owner, OwnerTally, comp_type
from .event2 import Activity, Fulfillment, Interest
from github2 import GithubWrapper
from coingecko import CoinWrapper

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

def notnull(self, attribute, value):
    if not value: # None and ''
        raise ValueError("Must not be empty")

def is_mainnet(self, attribute, value):
    if value != "mainnet":
        raise ValueError("Not mainnet")

@define(slots=False)
class Bounty(ToDictMixin):
    # underscore to exclude when exporting
    pk: int = field(validator=notnull, converter=to_int)
    _network: str = field(validator=is_mainnet)
    org_name: str = field(validator=notnull)
    url: str
    _paid: list
    _title: str
    _status: str
    _is_open: bool
    _keywords: str
    project_type: str
    bounty_type: str
    bounty_categories: list
    project_length: str
    experience_level: str
    permission_type: str
    token_name: str = field(validator=notnull)
    value_in_usdt: float = field(converter=to_float)
    _value_true: float = field(converter=to_float)
    _value_in_eth: float = field(converter=to_float)
    _value_in_token: float = field(converter=to_float)
    created: datetime = field(validator=notnull, converter=to_date)
    _expires_date: datetime = field(converter=to_date)
    _created_on: datetime = field(converter=to_date) 
    _modified_on: datetime = field(converter=to_date)
    _cancelled_on: datetime = field(converter=to_date)
    fulfillment_started_on: datetime = field(converter=to_date)
    fulfillment_submitted_on: datetime = field(converter=to_date)
    fulfillment_accepted_on: datetime = field(converter=to_date)
    
    github_url: str = field(validator=notnull)
    github_org_name: str = field(validator=notnull)
    github_issue_number: int = field(converter=to_int)
    github_repo_name: str
    github_comments: str
    github_issue_state: str
    bounty_owner_name: str
    _bounty_owner_email: str
    _bounty_owner_address: str
    bounty_owner_github_username: str

    _fulfillment: Fulfillment
    _interest: Interest
    _activity: Activity

    def update_events(self):
        self._fulfillment = self._update('fulfillment')
        self._interest = self._update('interest')
        self._activity = self._update('activity')
        self._owner = Owner.load(self.org_name)
        self._owner._update(self)
    
    def _update(self, event_type):
        _obj_lst = []
        events = getattr(self, f'_{event_type}')
        eventclass = get_eventclass(event_type)
        for event in events:
            event['pk'] = self.pk
            event_obj = eventclass.from_dict(event)
            event_obj.update()
            _obj_lst.append(event_obj)
        return _obj_lst
    
    def get_owner_attr(self, method):
        if self.org_name:        
            return getattr(OwnerTally.from_object(Owner.load(self.org_name), self.created), method)

    def get_user_attr(self, method):
        # self.user_stats = get_user_attrs()->UserWrapper object
        if self._interest:
            attrs = [getattr(UserTally.from_object(User.load(applicant.handle), self.created), method) for applicant in self._interest]
            return np.mean(attrs)

    def get_github_stats(self):
        self.github_stats = GithubWrapper.find(self.pk, self.created)
    
    def get_coin_stats(self):
        try: 
            self.coin_stats = CoinWrapper.setup(self.token_name, self.created)
        except FileNotFoundError:
            self.coin_stats = None

    @property
    def cancelled(self):
        '''or canceled_on is None'''
        return self._status=='cancelled'
    @property
    def submitted(self):
        return self.fulfillment_submitted_on is not None
    @property
    def accepted(self):
        return self.fulfillment_accepted_on is not None
    @property
    def num_interests(self):
        return len(self._interest)
    @property
    def num_fulfillments(self):
        return len(self._fulfillment)
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
                return (self.fulfillment_submitted_on - self._expires_date).days
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
    @property
    def github_owner_tenure(self):
        try:
            return (self.created - self.github_stats.org.created_at).days
        except (TypeError, AttributeError):
            return None
    @property
    def github_user_tenure(self):
        try:
            return (self.created - self.github_stats.user.created_at).days
        except (TypeError, AttributeError):
            return None
    