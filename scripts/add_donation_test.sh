#!/bin/bash

if [ $# -ne 2 ]; then
  echo -e "Usage:\n\tadd_donation_test.sh DONATION_ID USER_ID"
  exit 1
fi

curl \
  --data "id=${1}&user_id=${2}&object=sofa" \
  http://localhost:5000/api/add_donation
