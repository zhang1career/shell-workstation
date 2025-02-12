#!/bin/bash

# check argument cardinality
if [ $# -lt 5 ]; then
    echo "Usage: $0 <file_path> <redis_host> <redis_port> <prefix> <ttl>"
    exit 1
fi

file=$1
redis_host=$2
redis_port=$3
prefix=$4
ttl=$5

# check arguments
if [ ! -f "$file" ]; then
    echo "Error: File '$file' not found!"
    exit 1
fi

# cache data
while IFS=$'\t' read -r key value; do
    if [[ -n "$key" && -n "$value" ]]; then
        redis-cli -h "$redis_host" -p "$redis_port" SET "$prefix""$key" "$value" EX "$ttl"
    fi
done < "$file"
