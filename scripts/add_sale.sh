#!/bin/bash

if [ $# -ne 1 ]; then
  echo -e "Usage:\n\tadd_sale.sh DONATION_ID"
  exit 1
fi

curl --data "donation_id=${1}" http://localhost:5000/api/add_sale
