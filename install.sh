#! /bin/bash

apt-get install pmount

cp ./11-media-by-label-with-pmount.rules /etc/udev/rules.d/.

mkdir -p /etc/udev/scripts
cp ./minimal-update.sh /etc/udev/scripts/.
