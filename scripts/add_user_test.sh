#!/bin/bash

if [ $# -ne 1 ]; then
  echo -e "Usage:\n\tadd_user_test.sh USER_ID"
  exit 1
fi

curl \
  --data "id=${1}&name=Name&email=me@myself.org" \
  --data-urlencode "phone=+40768652156" \
  http://localhost:5000/api/add_user
