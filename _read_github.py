from datetime import date
from github2 import GithubWrapper
from attrs import asdict

GithubWrapper.load('github4.pkl')

pk_lst=[10189, 22642, 12345]
date = date(2020,1,1)

for pk in pk_lst:
    github = GithubWrapper.find(pk, date)
    github
    asdict(github)