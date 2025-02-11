#!/bin/bash

awk -F '\t' '{
    if ($2 != "None" && $2 != "")
        print $0
}' $1
