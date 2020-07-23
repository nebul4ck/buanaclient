# -*- coding: utf-8 -*-

"""
.. module:: main
   :platform: Unix/Linux
   :synopsis: Buanarepo-Client Tools class.
.. moduleauthor::
   :Nickname: nebul4ck
   :mail: a.gonzalezmesas@gmail.com
   :Web :
   :Version : 0.1.1
"""

import os
import sys
import json
import requests
import ast

from configobj import ConfigObj
from buanaclient.config.settings import DEPLOY_DIR, LANGUAGES, \
										CONFIG, CONFILE
from buanaclient.config.logger import logger as l

class buanaTools(object):
	"""docstring for buanaTools"""
	def __init__(self):
		super(buanaTools, self).__init__()
		self.confDir = DEPLOY_DIR
		self.languages = LANGUAGES
		self.confFile = CONFILE

	def loadProvisioning(self, provFile):

		err_out = ''

		provisionFile = '%s/%s' % (self.confDir, provFile)

		if not os.path.exists(provisionFile):
			err_out = 'Error: file %s not found!.' % provisionFile
			print(err_out)
			l.error(err_out)
			exit(1)
		else:
			config = ConfigObj(provisionFile)

			try:
				host_provisioning = config['hosts']
			except KeyError:
				err_out = 'Error: Section "hosts" not found!.'
				err_out += ' Please check your provisioning file.'
				print err_out
				l.error(err_out)
				exit(1)

		return host_provisioning

	def create_msg(self, fir_val, sec_val, ctrl):
		if ctrl == 'host':
			key1 = 'Host'
			key2 = 'Update'
		elif ctrl == 'service':
			key1 = 'Service'
			key2 = 'Install'

		cmd_stdout = {
						key2: sec_val,
						key1: fir_val
					}

		return cmd_stdout

	def test_language(self, language):
		if not language in self.languages:
			known = False
		else:
			known = True

		return known

	def listPackage(self, buanarepoUrl, buanaCA, basic_auth):
		''' Return available pakacges in BuanaServer '''
		msg_stdout = ''
		listpkg_command = '%s/get/listpkg' % buanarepoUrl
		msgerr = ''

		try:
			msg_stdout = requests.get(listpkg_command,
						verify=buanaCA, auth=basic_auth)
		except requests.exceptions.ConnectionError:
			msgerr = 'ERROR fetching buanaServer (%s) ' % buanarepoUrl
			msgerr +='\nmissing %s or unreachable remote server.' % buanaCA
			msgerr +='\nPlease, edit %s config file.' % self.confFile
			print(msgerr)
			l.error(msgerr)
			exit(1)
		except requests.exceptions.Timeout:
			msgerr = 'Error: Timeout raised!'
			print(msgerr)
			l.error(msgerr)
			exit(1)
		except requests.exceptions.HTTPError:
			msgerr = 'Error: Invalid HTTP response'
			print(msgerr)
			l.error(msgerr)
			exit(1)
		except requests.exceptions.TooManyRedirects:
			msgerr = 'Error: Maximum redirections exceeded!'
			print(msgerr)
			l.error(msgerr)
			exit(1)

		if msgerr:
			msg_stdout = msgerr

		return msg_stdout

	def try_install_pkg(self, pkg_list, data, buanarepoUrl, buanaCA):
		''' Check if a package can be installed'''
		l_packages = []
		pkg_not_found = []
		json_data = json.loads(data)

		try:
			all_packages = ast.literal_eval(pkg_list.text)

			""" Get from data, the services to deploy """
			for hosts, services in json_data.iteritems():
				for service in services:
					l_packages.append(service)

			for service in l_packages:
				available = service in all_packages

				if not available:
					pkg_not_found.append(service)

			if pkg_not_found:
				print('The next packages are not available:')
				for package in pkg_not_found:
					print('\t - %s' % package)

				print('\nPlease, edit deploy config file.')
				l_msg = 'Not all package set in deploy config file are available,'
				l_msg += ' please check it and run buanarepo again.'
				l.error(l_msg)

				can_do_it = False
			else:
				can_do_it = True
		except SyntaxError, e:
			msg = 'SSL: SSL_HANDSHAKE_FAILURE : You need CRT Client Auth.'
			msg += ' Contact with Buanarepo Support.'
			print msg
			l.error(msg)
			can_do_it = False
		except Exception:
			msg = 'It is impossible to verify the list of packages.'
			print msg
			l.error(msg)
			can_do_it = False

		return can_do_it
