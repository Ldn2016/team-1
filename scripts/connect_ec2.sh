#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ssh -i $DIR/team_1.pem force@52.211.153.190
