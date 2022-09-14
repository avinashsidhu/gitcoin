from github import Github, RateLimitExceededException, UnknownObjectException, GithubException
import logging
from functools import cached_property
import pickle
from pathlib import Path
from typing import ClassVar
from dataclasses import dataclass
import pytz
from tqdm import tqdm

def get_path(file):
    path = Path(file)
    path.touch(exist_ok=True)
    return path

def catch_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            response = func(self, *args, **kwargs)
            return response
        except AttributeError as err:  # preceding object is None
            message = f'(pk={self.pk}) {err}'
            logging.error(message)
        except UnknownObjectException as err: # err.status==404
            message = f'(pk={self.pk}) {err}'
            logging.error(message)
        except RateLimitExceededException as err:
            message = f'(pk={self.pk}) {err}'
            logging.error(message)
            logging.info(self.get_rate_limit_string())
            raise err
        except GithubException as err:
            if err.status==410: # disabled
                message = f'(pk={self.pk}) {err}'
                logging.error(message)
            else:
                message = f'(pk={self.pk}) {err}'
                logging.error(message)
                raise err
        
        return None
    return wrapper

@dataclass
class GithubGetter:
    g: ClassVar
    pk: int
    bounty_owner_github_username: str
    github_org_name: str
    github_repo_name: str
    github_issue_number: int

    @classmethod
    def get_rate_limit_string(cls):
        ratelimit = cls.g.get_rate_limit().core.remaining
        return f'{ratelimit} remaining. The limit will be reset at {cls.get_local_reset_time()}.'

    @classmethod
    def get_local_reset_time(cls):
        reset_time = cls.g.get_rate_limit().core.reset
        utc = reset_time.replace(tzinfo=pytz.timezone('UTC'))
        local = utc.astimezone(pytz.timezone('America/Detroit'))
        return local

    @classmethod
    def authenticate(cls, token):
        if token:
            cls.g = Github(token)
        else:
            cls.g = Github()
        logging.info(cls.get_rate_limit_string())

    # objects
    @cached_property
    @catch_error
    def org(self):
        return self.g.get_organization(self.github_org_name)
    @cached_property
    @catch_error
    def repo(self):
        return self.org.get_repo(self.github_repo_name)
    @cached_property
    @catch_error
    def issue(self):
        return self.repo.get_issue(self.github_issue_number)
    
    # rawdata
    @property
    @catch_error
    def org_rawdata(self):
        return self.org._rawData
    @property
    @catch_error
    def repo_rawdata(self):
        return self.repo._rawData
    @property
    @catch_error
    def forks_rawdata(self):
        # return [fork.created_at for fork in self.repo.get_forks()]
        return [fork._rawData for fork in self.repo.get_forks()]
    @property
    @catch_error
    def stars_rawdata(self):
        # return [star.starred_at for star in self.repo.get_stargazers_with_dates()]
        return [star._rawData for star in self.repo.get_stargazers_with_dates()]
    @property
    @catch_error
    def pulls_rawdata(self):
        # return [pull.created_at for pull in self.repo.get_pulls()]
        return [pull._rawData for pull in self.repo.get_pulls()]
    @property
    @catch_error
    def issue_rawdata(self):
        return self.issue._rawData
    @property
    @catch_error
    def issue_comments_rawdata(self):
        return [issue._rawData for issue in self.issue.get_comments()]
    @property
    @catch_error
    def user_rawdata(self):
        return self.g.get_user(self.bounty_owner_github_username)._rawData


class GithubLoader:
    _loaded = []
    _loaded_pk = []
    
    def __init__(self, response) -> None:
        self.pk = response.pk
        self.org = response.org_rawdata
        self.repo = response.repo_rawdata
        # self.forks = response.forks_rawdata
        # self.stars = response.stars_rawdata
        # self.pulls = response.pulls_rawdata
        self.issue = response.issue_rawdata
        # self.issue_comments = response.issue_comments_rawdata
        self.user = response.user_rawdata
        GithubLoader._loaded.append(self)
        logging.info(f'(pk={self.pk}) Success')

    @staticmethod
    def _read(f):
        try:
            file_data = pickle.load(f)
        except EOFError: # empty file
            file_data = []
        return file_data

    @classmethod  
    def to_pkl(cls, file):
        with get_path(file).open('r+b') as f:
            file_data = cls._read(f)
            for response in cls._loaded:
                file_data.append(response)
            f.seek(0)
            pickle.dump(file_data, f)
        
        # offload
        for instance in cls._loaded:
            cls._loaded_pk.append(instance.pk)
        if cls._loaded:
            message = f'{len(cls._loaded)} has been loaded in this session. {len(cls._loaded_pk)} instances in total.'
            logging.info(message)
        cls._loaded = []
    
    @classmethod
    def is_loaded(cls, pk: str):
        return pk in cls._loaded_pk
    
    @classmethod
    def restore(cls, file):
        with get_path(file).open('rb') as f:
            file_data = cls._read(f)
        cls._loaded_pk = [instance.pk for instance in file_data]
        logging.info(f'{len(cls._loaded_pk)} instances loaded.')
        return len(cls._loaded_pk)
        
    def __repr__(self):
        return f'GithubLoader(pk={self.pk})'

