# -*- coding: utf-8 -*-

import sys
import ast
import os.path
import configparser
import json

from buanaclient.config.logger import logger as l

# Delete this line after compiling

LANGUAGES = ['python', 'javascript', 'node', 'none']
APT_INSTALL = '/usr/bin/apt install -y'
APT_UPDATE = '/usr/bin/apt update'
USER_INSTALL = 'root'
HEADERS = {'content-type': 'application/json'}
CONFIG = {}
DEPLOY_DIR = '/etc/buanaclient'
CONFILE = ''

# Parse config file
CONFIG_FILE = '/etc/buanaclient/buanaclient.conf'
DEV_CONFIG_FILE = 'buanaclient.conf'

config = configparser.ConfigParser()
if os.path.isfile(CONFIG_FILE):
    config.read([CONFIG_FILE])
    CONFILE = CONFIG_FILE
elif os.path.isfile(DEV_CONFIG_FILE):
    l.info('Loading dev config file ./buanaclient.conf')
    config.read([DEV_CONFIG_FILE])
    CONFILE = DEV_CONFIG_FILE
else:
    l.critical(
        '- buanaclient - Configuration file not found (buanaclient.conf).')
    sys.exit(1)

buanaserver_host = ast.literal_eval(config['connection']['host'])
buanaserver_port = config.getint('connection', 'port')
buanaserver = 'https://%s:%d' % (buanaserver_host, buanaserver_port)
auth_user = ast.literal_eval(config['auth']['user'])
auth_passwd = ast.literal_eval(config['auth']['passwd'])
auth = { auth_user : auth_passwd }
auth_CA = ast.literal_eval(config['auth']['buanaServerCAcert'])


CONFIG['buanaServer'] = buanaserver
CONFIG['Auth'] = auth
CONFIG['auth_CA'] = auth_CA
