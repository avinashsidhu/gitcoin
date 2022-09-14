#!/bin/bash
cp /Users/kyunghee/Documents/GitHub/gitcoin/etc/local.github_scraper.plist ~/Library/LaunchAgents
lunchy restart local.github_scraper
lunchy status local.github_scraper
