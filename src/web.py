__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

import argparse
from conf_reader import ConfParser
import debug
from server import Server
import settings

"""
	Main server runner
"""


class Main(object):

	def __init__(self):
		self.parse_arguments()

	def parse_arguments(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-p', '--port', type=int, action='store', help='port the server will bind to', default=8000)
		parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging')
		self.args = parser.parse_args()

	def run(self):
		debug.debug = self.args.debug
		Server(self.args.port).run()


if __name__ == '__main__':

	# read in configuration
	tmp_settings = ConfParser().read_configuration()
	settings.HOSTS = tmp_settings['hosts']
	settings.MEDIA = tmp_settings['media']
	settings.TIMEOUT = tmp_settings['parameters']['timeout']

	m = Main()
	try:
		m.run()
	except KeyboardInterrupt:
		pass
