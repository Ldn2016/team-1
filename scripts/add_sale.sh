#!/bin/bash

if [ $# -ne 2 ]; then
  echo -e "Usage:\n\tadd_sale.sh DONATION_ID BUYER_ID"
  exit 1
fi

curl \
  --data "donation_id=${1}&amount=500GBP&buyer_id=${2}" \
  http://localhost:5000/api/add_sale
