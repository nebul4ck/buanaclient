#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import re
import socket
import json
#import requests

from buanaclient.lib import buanaClient
from buanaclient.config.logger import logger as l

def use():
  """ BUANACLIENT (client)
  usage: buanaclient <COMMAND> <CONFILE>|<APPLICATION> (develop|master) (--local|--remote>) (none|python|node)

  NAME
	buanaclient - BUilds ANd Adds to REPO.

  SYNOPSIS
	buanaclient <COMMAND> <CONFILE>|<APPLICATION> (develop|master) (--local|--remote>) (none|python|node)

  DESCRIPTION
	Buanaclient is the simple way to create backups (remote dirs and Github),
	builds .deb packages, adds .deb to a central repository (continuous delivery)
	and servers provisioning.

  COMMANDS
	backup  - Synchronizes directories.
	git   - Get a copy of an existing Git repository and builds the .deb package.
	mpkg  - Build package from Jenkins sources.
	deploy  - Servers provisioning.
	list  - Show available packages in BuanaServer.

  KNOWN LANGUAGES
	If use either git or mpkg commands, they will build debian package in BuanaServer. Automatically
	BuanaServer upload two packages to repository (a plain code program and another program with
	encrypted code). To encrypt the code will be necessary known the development language, ie:

	  # buanaclient git|mpkg <repo_name> python|node

  DEPLOY MODES
	--local    - Buanaclient is installed in localbox. Install commands will be launch
		   in localhost. In this case, buanaclient will be install into each server
		   where you want install services.
	--remote   - Buanaclient is installed in orchestrator's server (agent). Install
		   commands will be launch from agent.

  CONFILE
	The name of the configuration file for provisioning. Is necessary create a
	configuration file into /etc/buanarepo/client or modify the template
	(deploy-server.conf.template)

	To run backups will be necessary edit /etc/buanarepo/client/buanaconfig.conf

  APPLICATION
	The name of application to sync and builds the package

  EXAMPLES

	foobar = appname

	$ buanaclient list
	$ buanaclient backup foobar
	$ buanaclient git foobar develop|master python|node|none
	$ buanaclient mpkg foobar develop|master python|node|none
	$ buanaclient deploy deploy.conf --local|--remote
	$ buanaclient sync releasing master
  """

def run_agent(command, arg_cmd, opt, client_host, branch='develop'):

	buanarepo_main = buanaClient.buanaClient()
	run_prg = buanarepo_main.start_program(command, arg_cmd, opt, \
										client_host, branch)

	return run_prg

""" Global vars """
num_params = len(sys.argv)
client_host = socket.getfqdn()

""" Runs buanarepo-client """
if num_params <= 1:
	help(use)
	exit(1)

command = sys.argv[1]
opt = ''
branch = 'default'

# Fix ñapa with args parse please!

if command == 'git' or command == 'mpkg':
	if num_params is not 5:
		help(use)
		exit(1)
	else:
		arg_cmd = sys.argv[2]
		branch = sys.argv[3]
		opt = sys.argv[4]
elif command == 'deploy' or command == 'sync':
	if num_params is not 4:
		help(use)
		exit(1)
	else:
		arg_cmd = sys.argv[2]
		if command == 'sync':
			branch = sys.argv[3]
			opt = None
		else:
			opt = sys.argv[3]
elif command == 'list':
	if num_params is not 2:
		help(use)
		exit(1)
	else:
		arg_cmd = None
elif command == 'pip2deb':
	if num_params is not 3:
		help(use)
		exit(1)
	else:
		arg_cmd = sys.argv[2]
else:
	if num_params is not 3:
		help(use)
		exit(1)

run_command = run_agent(command, arg_cmd, opt, client_host, branch)
print run_command
