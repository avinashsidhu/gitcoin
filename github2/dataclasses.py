import re, datetime, pickle, bisect
from helpers import get_path, ToDictMixin, to_date
from attrs import define, field
from typing import ClassVar

def custom_repr(self):
    items = [f'{k}={v}' for k, v in self.__dict__.items()]
    return f'{type(self).__name__}({",".join(items)})'

def count_before_date(lst, attr, date):
    dates = [to_date(i.get(attr)) for i in lst]
    dates.sort()
    return bisect.bisect_left(dates, date)

@define(slots=False)
class GithubOrg(ToDictMixin):
    user: str
    created_at: datetime = field(converter=to_date)
    followers: str
    following: str
    public_repos: str
    
    @classmethod
    def from_dict(cls, org):
        return cls(org['login'], org['created_at'], org['followers'], org['following'], org['public_repos'])

@define(slots=False)
class GithubUser(GithubOrg):
    twitter_username: str    

    @classmethod
    def from_dict(cls, org):
        return cls(org['login'], org['created_at'], org['followers'], org['following'], org['public_repos'], org['twitter_username'])

@define(slots=False)
class GithubRepo(ToDictMixin):
    date: str
    owner: str
    forks_count: int
    stars_count: int
    # stars_count_all: int
    # pulls_count: int

    @classmethod
    def from_dict(cls, repo, date):
        return cls(
            date,
            repo['owner']['login'],
            repo['forks_count'],
            # count_before_date(forks, 'created_at', date),
            # count_before_date(stars, 'starred_at', date),
            repo['stargazers_count']
            # count_before_date(pulls, 'created_at', date)
        )

@define(slots=False)
class GithubIssue(ToDictMixin):
    comments_count: int
    # status: str

    @classmethod
    def from_dict(cls, issue):
        try: 
            comments_count = issue['comments']
            return cls(
                comments_count
                # cls.get_status(issue_comments)
            )
        except KeyError: 
            # invalid issue response
            return None
            
    @staticmethod
    def get_status(issue_comments)->str:
        '''
        Extract status from gitcoinbot's comment
        Issue Status: 1. **Open** 2. Started 3. Submitted 4. Done --> status: open
        '''
        gitcoinbot_comments = [i for i in issue_comments if i['user']['login']=='gitcoinbot']
        gitcoinbot_comments.sort(key=lambda x: x['created_at'])
        try:
            recent = gitcoinbot_comments[-1]
        except IndexError:
            # no gitcoinbot comment
            return None
        try:
            query = '[0-9]. \\*\\*([a-zA-Z]+)\\*\\*'
            return re.findall(query, recent['body'])[0].lower()
        except IndexError:
            return None

@define(slots=False)
class GithubWrapper(ToDictMixin):
    _data: ClassVar = None
    org: GithubOrg
    repo: GithubRepo
    issue: GithubIssue
    user: GithubUser

    @classmethod
    def load(cls, data_file):
        with get_path('data', data_file).open('rb') as f:
            cls._data = pickle.load(f)
    @classmethod            
    def find(cls, pk, date):
        search_result = [instance for instance in cls._data if instance.pk==pk]
        if len(search_result)>=1: # more than one?
            github = search_result[0]
            return cls(
                GithubOrg.from_dict(github.org) if github.org else None,
                GithubRepo.from_dict(github.repo, date) if github.repo else None,
                GithubIssue.from_dict(github.issue) if github.issue else None,
                GithubUser.from_dict(github.user) if github.user else None
            )
        else:
            raise IndexError("No Github instance matched with provided pk")