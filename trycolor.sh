#!/bin/bash

# We don't want while read LINE to eat our leading whitespace
IFS=''
while read LINE; do
	res=$(echo "${LINE}" | sed \
		-e s/'\] \[PASS\]$'/'\] \[\\e\[32mPASS\\e\[00m\]'/ \
		-e s/'\] \[FAIL\]$'/'\] \[\\e\[1;91mFAIL\\e\[00m\]'/ \
		-e s/'\] \[KILLED\]$'/'\] \[\\e\[1;101mKILLED\\e\[00m\]'/ \
		-e s/'\] \[SKIP\]$'/'\] \[\\e\[1mSKIP\\e\[00m\]'/ \
		-e s/'\] \[RERAN\]$'/'\] \[\\e\[1;93mRERAN\\e\[00m\]'/ \
		-e s/'^\(PASS\W\)'/'\\e\[1;92m\1\\e\[00m'/ \
		-e s/'^\(FAIL\W\)'/'\\e\[1;91m\1\\e\[00m'/ \
		-e s/'^\(KILLED\W\)'/'\\\e\[1;101m\1\\e\[00m'/ \
		-e s/'^\(SKIP\W\)'/'\\e\[1m\1\\e\[00m'/ \
		-e s/'^\(RERAN\W\)'/'\\e\[1;93m\1\\e\[00m'/ \
		-e s/'^Tests\ with\ result\(.\+\)PASS\(.\+\)$'/'Tests with result\1\\e\[1;92mPASS\\e\[00m\2'/ \
		-e s/'^\(\W\+\)\(KILLED\)\(\W\)'/'\1\\e\[1;101m\2\\e\[00m\3'/g \
		-e s/'^\(\W\+\)\(FAIL\)\(\W\)'/'\1\\e\[1;91m\2\\e\[00m\3'/g \
		-e s/'^\(\W\+\)\(RERUN\)\(\W\)'/'\1\\e\[1;93m\2\\e\[00m\3'/g \
		-e s/'^\(\W\+\)\(SKIP\)\(\W\)'/'\1\\e\[1m\2\\e\[00m\3'/g \
		-e s/'expected \(PASS\))$'/'expected \\e\[1;92m\1\\e\[00m)'/ \
		-e s/'expected \(KILLED\))$'/'expected \\e\[1;101m\1\\e\[00m)'/ \
		-e s/'expected \(FAIL\))$'/'expected \\e\[1;91m\1\\e\[00m)'/ \
		-e s/'expected \(RERUN\))$'/'expected \\e\[1;93m\1\\e\[00m)'/ \
		-e s/'expected \(SKIP\))$'/'expected \\e\[1m\1\\e\[00m)'/ \
		-e s/'^Test\( ([A-Za-z0-9 ]\+)\)\?: \(.\+\) (run as \(.\+\)) \[\([0-9]\+:[0-9]\+\)\] \[\(.\+\)\]$'/'\\e\[1mTest\1: \\e\[0m\2 (\\e\[1mrun as \3\\e\[0m) \[\\e\[1m\4\\e\[0m\] \[\5\]'/ \
	)
	echo -e "${res}"
done