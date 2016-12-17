__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

from wsgiref.handlers import format_date_time
from datetime import datetime
import debug
from time import mktime
import settings
from http_consts import STATUS_MSG_MAP


class HttpResponse(object):

	status_code = 200

	def __init__(self, status=None, content_f='pages/index.html', method='GET', h_range=None):
		now = datetime.now()
		stamp = mktime(now.timetuple())

		if status is not None:
			self.status_code = status
		self.server = 'SwagSwerver'
		self.date = format_date_time(stamp)
		self.content_type = settings.MEDIA[content_f.split('.')[-1]]
		with open(content_f) as f:
			if self.status_code == 206:
				spl_range = h_range.replace('bytes=', '').split('-')
				start = int(spl_range[0])
				end = int(spl_range[1])
				self.content = f.read()[start:end+1]
			else:
				self.content = f.read()
		self.content_length = len(self.content)
		self.last_modified = None
		self.method = 'GET'

	def __str__(self):
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


class HttpResponsePartialContent(HttpResponse):
	status_code = 206


class HttpResponseBadRequest(HttpResponse):
	status_code = 400


class HttpResponseForbidden(HttpResponse):
	status_code = 403


class HttpResponseNotFound(HttpResponse):
	status_code = 404


class HttpResponseServerError(HttpResponse):
	status_code = 500


class HttpResponseNotImplemented(HttpResponse):
	status_code = 501
