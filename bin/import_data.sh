#!/bin/bash

echo "`date`: beginning data load"

# In text mode, COPY will crash when confronting a backslash in JSON, and there is no option to specify a different escape charcter in text mode.
# Instead, use CSV mode, with quote and delimiter set to something that never appear in JSON. So that the whole line is considered as one data tandum.
# http://adpgtech.blogspot.com/2014/09/importing-json-data.html

cat data/data.json | jq -c '.[]' | psql gitcoin -c "COPY bounty (data) FROM stdin csv quote e'\x01' delimiter e'\x02';"

echo "`date`: populated data"

