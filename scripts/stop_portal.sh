#!/bin/bash

set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# stop the DHCP service, AP service, and IP Tables redirects
systemctl stop hostapd.service
systemctl stop dnsmasq.service

# remove the interface
if ip link ls up | grep -q 'uap0' &> /dev/null; then
    iw dev uap0 del
fi

# remove the captive portal thing
iptables -t nat -A PREROUTING -F

