from wsgiref.handlers import format_date_time
from datetime import datetime
import debug
from time import mktime
from http_consts import STATUS_MSG_MAP


class Response():

	def __init__(self, status=200, content='asdfasdf', f_type='text'):
		now = datetime.now()
		stamp = mktime(now.timetuple())

		self.status_code = status
		self.server = 'DrekSwerver (Mint)'
		self.date = format_date_time(stamp)
		self.content_type = f_type
		self.content_length = len(content)
		self.last_modified = None

	def get_response_str(self):
		protocol_string = 'HTTP/1.1 %i %s' % (self.status_code, STATUS_MSG_MAP[self.status_code])
		server_string = 'Server: %s' % self.server
		date_string = 'Date: %s' % self.date
		content_type_string = 'Content-Type: %s' % self.content_type
		content_length_string = 'Content-Length: %i' % self.content_length

		main_str = ''
		main_str += protocol_string + '\r\n'
		main_str += server_string + '\r\n'
		main_str += date_string + '\r\n'
		main_str += content_type_string + '\r\n'
		main_str += content_length_string + '\r\n'

		main_str += '\r\n'
		return main_str
