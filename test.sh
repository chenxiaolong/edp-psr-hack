#!/bin/bash

set -xeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

make

sudo /lib/modules/"$(uname -r)"/build/scripts/sign-file \
    sha256 \
    "${SIGNING_KEY:-/usr/share/secureboot/keys/db/db.key}" \
    "${SIGNING_CERT:-/usr/share/secureboot/keys/db/db.der}" \
    edp-psr-hack.ko

sudo rmmod edp-psr-hack || :
sudo insmod edp-psr-hack.ko
