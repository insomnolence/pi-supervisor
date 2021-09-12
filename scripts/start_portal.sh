#!/bin/bash

set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# ensure the AP interface is ready to go and reset as needed
if ip link ls up | grep -q 'uap0' &> /dev/null; then
    iw dev uap0 del
fi

iw dev wlan0 interface add uap0 type __ap && \
    ifconfig uap0 172.31.0.1 netmask 255.255.255.0 up

# do the captive portal thing
iptables -t nat -A PREROUTING -i uap0 -p tcp --dport 80 -j DNAT  --to-destination  172.31.0.1:8000
iptables -t nat -A PREROUTING -i uap0 -p tcp --dport 430 -j DNAT --to-destination  172.31.0.1:8443

# start the DHCP service, AP service, and IP Tables redirects
systemctl start hostapd.service
sleep 2
systemctl start dnsmasq.service
