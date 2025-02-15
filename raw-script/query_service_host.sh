#!/bin/bash

# check arguments cardinality
if [ $# -lt 1 ]; then
  echo "Usage: $0 [redis-key] [default-value]"
  exit 1
fi

# get arguments
REDIS_KEY=$1
DEFAULT_VALUE=""
if [ $# -ge 2 ]; then
  DEFAULT_VALUE=$2
fi

# query redis
VALUE=$(redis-cli GET "reg:serv:$REDIS_KEY")
# use default value if not found
if [ -z "$VALUE" ]; then
  echo "$DEFAULT_VALUE"
  exit 0
fi

# get the first part
FIRST_PART=$(echo "$VALUE" | cut -d ':' -f 1)

echo "$FIRST_PART"