#!/bin/bash

# Easy way to quickly add more tests using real API data.
# Please only use advisories that have already shipped live.

set -ex

if [ -z $1 ]; then
  echo "Specify an ET API URL."
  echo "Examples:"
  echo "  https://errata.devel.redhat.com/advisory/26175.json"
  echo "  https://errata.devel.redhat.com/api/v1/erratum/26175"
  echo "Please only use advisories that have already shipped live."
  exit 1
fi

URL=$1

FIXTURE=$(echo $URL | sed 's|^https://||')
DIRNAME=$(dirname $FIXTURE)

cd errata_tool/tests/fixtures/
mkdir -p $DIRNAME
curl -g --negotiate -u : -q $URL > $FIXTURE

git add $FIXTURE
