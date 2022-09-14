# Gitcoin
Gitcoin project repo  

## Description
* `coingecko/`: coingecko scraper and Coin class
* `gitcoin/`: classes for Gitcoin objects
* `github2/`: github scraper and classes for Github objects
* `ado/`: custom STATA ado  
* `helpers.py`
* `profile.do`

[Currently not being used]  
* `bin/`: shell script
* `sql/`: script to create NOSQL schema

## Dependencies
```
pipenv install
```

## Usage
```
pipenv shell

# run scrappers (the results will be save to var/cache)
python gitcoin_scraper.py
python github_scraper.py
python coingecko_scraper.py

# compile data
python read_bounties.py

# run analysis on STATA
stataMP-64 -e do anlys.do
```


