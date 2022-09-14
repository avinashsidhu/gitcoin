#!/bin/bash

createdb gitcoin
psql gitcoin -f sql/create_schema.sql