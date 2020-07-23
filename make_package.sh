#!/bin/bash

set -u -e -o pipefail

# PATHS
JENKINS_BASE="/var/lib/jenkins/workspace"
BASE="."

help() {
	echo "Usage: ./make_package.sh python_version make_mode repository"
	echo "python_version: [2.7|3.6|3.7] jenkins|local buanaclient"
	exit 1
}

if [ $# -ne 3 ]; then
	help
else
	PYTHON_VERSION=$1
	SET_MODE=$2
	REPO=$3

	if [ $SET_MODE == "jenkins" ]; then
		BASE="${JENKINS_BASE}/${REPO}"
	fi	
fi

rsync -av --delete -r --exclude '*pyc' ./src/buanaclient/* ${BASE}/buanaclient/usr/lib/python${PYTHON_VERSION}/dist-packages/buanaclient/
cp ./src/buanaclient.conf-prod ${BASE}/buanaclient/etc/buanaclient/buanaclient.conf && echo "buanaclient.conf-prod file sent"
cp ./src/logging.conf-prod ${BASE}/buanaclient/etc/buanaclient/logging.conf && echo "logging.conf-prod file sent"
cp ./src/buanaclient.py ${BASE}/buanaclient/usr/bin/buanaclient && echo "buanaclient.py file sent"
chmod +x ${BASE}/buanaclient/usr/bin/buanaclient && echo "attr changed!"


