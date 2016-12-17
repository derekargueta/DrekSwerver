__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

EXPECTED_COMPONENTS_PER_LINE = 3


class ConfParser(object):
	
	def __init__(self):
		self.conf_map = {
			'host': self._parse_host,
			'media': self._parse_media,
			'parameter': self._parse_parameter
		}

		self.settings = {
			'hosts': {},
			'media': {},
			'parameters': {}
		}

	def _parse_host(self, spl_line):
		self.settings['hosts'][spl_line[1]] = spl_line[2]

	def _parse_media(self, spl_line):
		self.settings['media'][spl_line[1]] = spl_line[2]

	def _parse_parameter(self, spl_line):
		self.settings['parameters'][spl_line[1]] = spl_line[2]

	def _parse_line(self, line):
		split_line = line.replace('\n', '').split(' ')
		assert len(split_line) == EXPECTED_COMPONENTS_PER_LINE
		configuration_key = split_line[0]
		try:
			# ok not gonna lie, this is pretty cool. Looking up the appropiate 
			# parsing function per key
			self.conf_map[configuration_key](split_line)
		except KeyError:
			print('Bad configuration file, found unrecognized key %s' % configuration_key)

	def read_configuration(self):

		try:
			with open('web.conf') as f:
				for line in f:

					# skip blank lines
					if len(line) > 2:
						self._parse_line(line)

		except IOError:
			print('Unable to open server configuration. Using defaults')
			# TODO - set up defaults

		return self.settings
