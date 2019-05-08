#!/bin/bash
domain=$1

ping $domain -c1
if ["$?" = 0]; then
  echo Successful
else
  echo Failure
fi
