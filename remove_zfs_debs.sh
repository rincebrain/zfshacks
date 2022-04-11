#!/bin/bash
pkgs="$(dpkg -l | awk '{ print $2 }' | egrep '(^libnvpair|^libuutil|^kmod-spl|^kmod-zfs|^libzpool|^libzfs|pyzfs$|^zfs|^spl)' | while read LINE;do echo -n $LINE\ ;done;)"
#echo $pkgs;
if [ "x${pkgs}" != "x" ]; then
	apt remove -y ${pkgs}
	pkgs="$(dpkg -l | awk '{ print $2 }' | egrep '(^libnvpair|^libuutil|^kmod-spl|^kmod-zfs|^libzpool|^libzfs|pyzfs$|^zfs|^spl)' | while read LINE;do echo -n $LINE\ ;done;)"
	if [ "x${pkgs}" != "x" ]; then
		apt purge -y ${pkgs}
	fi
fi
