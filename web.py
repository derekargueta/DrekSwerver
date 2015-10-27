__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

import argparse
import debug
from server import Server


class Main(object):

	def __init__(self):
		self.parse_arguments()

	def parse_arguments(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-p', '--port', type=int, action='store', help='port the server will bind to', default=8080)
		parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging')
		self.args = parser.parse_args()

	def run(self):
		debug.debug = self.args.debug
		s = Server(self.args.port)
		s.run()


if __name__ == '__main__':
	m = Main()
	try:
		m.run()
	except KeyboardInterrupt:
		pass