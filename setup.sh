#!/bin/bash 
set -eo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# install applications
export DEBIAN_FRONTEND=noninteractive
apt-get update -q 
apt-get full-upgrade -qy
apt-get install -qy hostapd dnsmasq

# Radio management
rfkill unblock wlan

# create folders, copy files, and install the modules
if [[ ! -d /usr/local/lib/supervisor ]]; then 
    mkdir -p /usr/local/lib/supervisor
fi

# create a user if it doesn't exist
if ! getent passwd supervisor > /dev/null 2>&1; then
    useradd -r -d /usr/local/lib/supervisor -s /bin/bash supervisor
fi
# add sudoers file
cp 090_supervisor /etc/sudoers.d && chmod 700 /etc/sudoers.d/090_supervisor

# Add the dhcp setup
cp "${DIR}/supervisor-dhcp.conf" /etc/dnsmasq.d && chmod 644 /etc/dnsmasq.d/supervisor-dhcp.conf

# add services file and setup systemd
cp "${DIR}/supervisor.service" /etc/systemd/system && chmod 644 /etc/systemd/system/supervisor.service
cp "${DIR}/hostapd.conf" /etc/hostapd && chmod 600 /etc/hostapd/hostapd.conf
systemctl daemon-reload && systemctl enable supervisor.service
systemctl unmask hostapd.service