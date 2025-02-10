#!/bin/bash

# git commit with tag
# cd fusio-adapter-http for example
# tag a new number greater than before
gta 'v6.0.8.xx' -m 'version 6.0.8.xx'

# push the commit along with the tag
gpoat

# login a deployed servcie
# cd fusio
cd /data/fusio
# upgrade the depencied code
composer update fusio/adapter-http
