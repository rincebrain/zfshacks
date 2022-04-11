#!/bin/bash
pkgs="$(rpm -qa | egrep '(^libnvpair|^libuutil|^kmod-spl|^kmod-zfs|^libzpool|^libzfs|pyzfs|^zfs|^spl)' | while read LINE;do echo -n $LINE\ ;done;)"
#echo $pkgs;
if [ "x${pkgs}" != "x" ]; then
	dnf remove -y ${pkgs}
fi
