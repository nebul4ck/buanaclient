# -*- coding: utf-8 -*-

"""
.. module:: main
   :platform: Unix/Linux
   :synopsis: Buanarepo-Client main class.
.. moduleauthor::
   :Nickname: nebul4ck
   :mail: a.gonzalezmesas@gmail.com
   :Web :
   :Version : 0.1.3
"""

import os
import requests
import json
import getpass
import re

from buanaclient.lib import buanaTools
from buanaclient.config.settings import APT_INSTALL, APT_UPDATE, \
						USER_INSTALL, HEADERS, LANGUAGES, CONFIG
from buanaclient.config.logger import logger as l

from multiprocessing import *
from subprocess import PIPE, Popen, CalledProcessError

class buanaClient(object):
	"""Buanarepo-Client main methods"""
	def __init__(self):
		super(buanaClient, self).__init__()
		self.apt_install = APT_INSTALL
		self.apt_update = APT_UPDATE
		self.user_install = USER_INSTALL
		self.headers = HEADERS
		self.languages = LANGUAGES
		self.buanarepoServerUrl = CONFIG['buanaServer']
		self.buanauth = CONFIG['Auth']
		self.buanaCA = CONFIG['auth_CA']
		self.client_tools = buanaTools.buanaTools()

	def start_program(self, command, client_host, opt, arg_cmd, branch):
		''' Initialize buanaclient '''
		msg_err = ''
		msg_stdout = ''
		l_deploy = ''
		r_deploy = ''

		user_auth, passwd_auth = self.buanauth.items()[0]
		basic_auth = (user_auth, passwd_auth)

		if re.findall(r'not found', str(self.buanarepoServerUrl)):
			msg_err = self.buanarepoServerUrl
		else:
			if command == 'deploy':
				deploy_mode = opt
				l_deploy, r_deploy = self.deployer(command,
										arg_cmd, deploy_mode,
										self.buanarepoServerUrl,
										basic_auth, self.buanaCA)
			elif command == 'git' or command == 'mpkg':

				git_data = self.test_git(client_host, arg_cmd, branch, opt)

				try:
					""" Sends post to remote Git deploy """
					r_deploy = self.buanaRemoteDeploy(
								git_data, basic_auth, self.buanaCA,
								self.buanarepoServerUrl, command)
				except Exception, e:
					print e
					l.error(e)
					msg_err = e
			elif command == 'backup':
				app = arg_cmd

				json_data = {
							'host': client_host,
							'app': app
							}

				data = json.dumps(json_data)

				try:
					""" Sends post to remote deploy """
					r_deploy = self.buanaRemoteDeploy(
								data, basic_auth, self.buanaCA,
								self.buanarepoServerUrl, command)
				except Exception, e:
					print e
					l.error(e)
					msg_err = e
			elif command == 'list':
				r_deploy = self.client_tools.listPackage(
							self.buanarepoServerUrl, self.buanaCA, basic_auth)
			else:
				msg_err = '"%s" is not a valid command.' % command
				msg_err +=' Try with backup, git or deploy.'

			if not msg_err:
				if r_deploy:
					try:
						return_msg = r_deploy.text
						http_code = int(r_deploy.status_code)

						if http_code != 200:
							err_code = '\nHTTP CODE ERROR: %s' % str(http_code)
							msg_err = '%s\n%s' % (err_code, return_msg)
						else:
							msg_stdout = '\n%s' % return_msg
					except AttributeError, e:
						msg_err = e
				elif l_deploy:
					msg_stdout = l_deploy

		if msg_err:
			msg_stdout = msg_err

		return msg_stdout

	def deployer(self, command, arg_cmd, deploy_mode, url, basic_auth, buanaCA):

		deploy_stdout = []
		l_deploy = ''
		r_deploy = ''

		file = arg_cmd
		provisioningFile = self.client_tools.loadProvisioning(file)
		buanarepoServerUrl = url

		if re.findall(r'not found', str(provisioningFile)):
			# return provisioningFile
			msg_stdout = provisioningFile
			print msg_stdout
			l.error(msg_stdout)
			exit(1)
		else:
			data = json.dumps(provisioningFile)

			# Check if it is a either local or remote deploy
			if deploy_mode == '--local':
				# Local deploy
				""" Sends local apt install command """
				l_deploy = self.buanaLocalDeploy(
					data, basic_auth, buanaCA, buanarepoServerUrl)
			elif deploy_mode == '--remote':
				# Remote deploy
				""" Sends post to remote deploy"""
				r_deploy = self.buanaRemoteDeploy(
					data, basic_auth, buanaCA, buanarepoServerUrl, command)
			else:
				msg_err = 'Deploy mode must be either "--local" or'
				msg_err += '"--remote", please, try again.'
				print msg_err
				l.error(msg_err)
				exit(1)

		deploy_stdout.extend([l_deploy, r_deploy])

		return  deploy_stdout

	def test_git(self, client_host, app, branch, language):

		language_is_known = self.client_tools.test_language(language)

		if not language_is_known:
			l.error('Select a valid language: %s' % self.languages)
			print('Select a valid language: %s' % self.languages)
			exit(1)

		json_data = {
			'host': client_host,
			'app': app,
			'branch': branch,
			'language' : language
			}

		data = json.dumps(json_data)

		return data

	def orchestrator(self, host, services, l_msg):

		""" Install pkgs in local mode (only root user) """

		user = getpass.getuser()
		if user != self.user_install:
			msg_action = "Only root can install pkgs. Bye bye..."
		else:
			msg_action = []
			proc = os.getpid()
			try:
				p = Popen(self.apt_update, stdout=PIPE, stderr=PIPE, shell=True)
				command_stdout, command_stderr = p.communicate()
				if command_stdout:
					print('Stdout: %s' % command_stdout)
					command_stdout = 'Update apt source list done.'
				else:
					print('Stderr: %s' % command_stderr)
			except CalledProcessError as e:
				command_stderr = e.output

			if command_stdout:
				msg_action.append(command_stdout)
			else:
				msg_action.append(command_stderr)

			for service in services:
				ins_cmd = '%s %s' % (self.apt_install, service)

				try:
					p = Popen(ins_cmd, stdout=PIPE, stderr=PIPE, shell=True)
					command_stdout, command_stderr = p.communicate()

					if command_stdout:
						print('Stdout: %s' % command_stdout)
						command_stdout = 'Service %s installed.' % service
					else:
						print('Stderr: %s' % command_stderr)

				except CalledProcessError as e:
					command_stderr = e.output

				if command_stdout:
					msg_action.append(command_stdout)
				else:
					msg_action.append(command_stderr)

			msg_action = {'Host': host, 'Install': msg_action}

		l_msg.append(msg_action)

	def buanaLocalDeploy(self, data, basic_auth, buanaCA, buanarepoUrl):

		jobs = []
		msg_action = []
		manager = Manager()
		l_msg = manager.list()
		json_data = json.loads(data)
		pkg_list = self.client_tools.listPackage(buanarepoUrl,
													buanaCA, basic_auth)
		can_do_it = self.client_tools.try_install_pkg(pkg_list,
												data, buanarepoUrl, buanaCA)

		if can_do_it is not True:
			l_msg = 'Exiting from local deploying mode... Bye.'
		else:
			for host, services in json_data.iteritems():

				p = Process(name='orchestration-host', target=self.orchestrator,
					args=(host, services, l_msg))
				jobs.append(p)
				p.start()

				for proc in jobs:
					proc.join()

		return l_msg

	def buanaRemoteDeploy(self, data, basic_auth, buanaCA, buanarepoUrl, command):

		headers = self.headers
		msgerr = ''
		send_post = ''
		can_do_it = True

		if command == 'deploy':
			pkg_list = self.client_tools.listPackage(buanarepoUrl,
														buanaCA, basic_auth)
			can_do_it = self.client_tools.try_install_pkg(pkg_list,
													data, buanarepoUrl, buanaCA)
			runner_command = '%s/run/%s' % (buanarepoUrl, command)
		else:
			runner_command = '%s/make/%s' % (buanarepoUrl, command)

		if can_do_it is not True:
			msgerr = 'Exiting from remote deploying mode... Bye.'
		else:
			try:
				# Verify = 'path/to/CA.crt'. The CA who signed the buanarepo-server certs
				send_post = requests.post(runner_command, verify=buanaCA,
										headers=headers, data=data, auth=basic_auth)
				msgerr = send_post.raise_for_status()
			except Exception as e:
				print e
				l.error(e)
			except requests.exceptions.ConnectionError:
				msgerr = 'Error: Check host connection. Edit buanaconfig file.'
				print msgerr
				l.error(msgerr)
				exit(1)
			except requests.exceptions.Timeout:
				msgerr = 'Error: Timeout raised!'
				print msgerr
				l.error(msgerr)
				exit(1)
			except requests.exceptions.HTTPError:
				msgerr = 'Error: Invalid HTTP response'
				print msgerr
				l.error(msgerr)
				exit(1)
			except requests.exceptions.TooManyRedirects:
				msgerr = 'Error: Maximum redirections exceeded!'
				print msgerr
				l.error(msgerr)
				exit(1)

		if not msgerr:
			msg_action = send_post
		else:
			msg_action = msgerr

		return msg_action
