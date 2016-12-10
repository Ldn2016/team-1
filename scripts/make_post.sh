#!/bin/bash

if [ $# -ne 1 ]; then
  echo -e "Usage:\n\tmake_post.sh USER_ID"
  exit 1
fi

curl --data "id=${1}&name=Calin&phone=0768652156&email=me@myself.org" \
  http://localhost:5000/api/add_user
