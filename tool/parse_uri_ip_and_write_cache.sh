#!/bin/bash

# check argument cardinality
if [ $# -lt 4 ]; then
    echo "Usage: $0 <file_path> <redis_host> <redis_port> <ttl>"
    exit 1
fi

file=$1
redis_host=$2
redis_port=$3
ttl=$4

# check arguments
if [ ! -f "$file" ]; then
    echo "Error: File '$file' not found!"
    exit 1
fi

# cache data
while IFS=$'\t' read -r key value; do
    if [[ -n "$key" && -n "$value" ]]; then
        redis-cli -h "$redis_host" -p "$redis_port" SET "$key" "$value" EX "$ttl"
    fi
done < "$file"

echo "Success."
