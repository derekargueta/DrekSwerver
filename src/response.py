__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

from wsgiref.handlers import format_date_time
from datetime import datetime
from debug import debug_print
from time import mktime
import settings
from http_consts import STATUS_MSG_MAP
import os
import hashlib


def file_is_binary(filepath: str) -> bool:
	# we're going to treat HTML and TXT as the defacto non-binary file types but
	# there should be a more robust way to do this.
	txt_file_types = ['txt', 'html']
	_, extension = os.path.splitext(filepath)
	return extension not in txt_file_types


def etag_for_file(filepath: str):
	m = hashlib.sha1()
	hash_str = filepath + str(os.path.getmtime(filepath))
	m.update(hash_str.encode('utf-8'))
	return m.hexdigest()[:14]


class HttpResponse(object):

	status_code = 200

	def __init__(self, status=None, content_f='pages/index.html', method='GET', h_range=None):
		if status is not None:
			self.status_code = status
		self.server = 'SwagSwerver'
		self.date = self._get_date_header_value()
		print('{0} - Serving {1}'.format(self.date, content_f))
		self.content_type = settings.MEDIA[content_f.split('.')[-1]]

		if self.status_code != 304:
			f_mode = 'r'
			if file_is_binary(content_f):
				f_mode += 'b'
			with open(content_f, f_mode) as f:
				if self.status_code == 206:
					spl_range = h_range.replace('bytes=', '').split('-')
					start = int(spl_range[0])
					end = int(spl_range[1])
					self.content = f.read()[start:end+1]
				else:
					self.content = f.read()
			self.content_length = len(self.content)
		else:
			self.content_length = 0
		self.last_modified = None		# TODO: impl
		self.method = 'GET'
		self.hash = etag_for_file(content_f)

	def _get_date_header_value(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		return format_date_time(stamp)

	def __str__(self) -> str:
		''' Produces the HTTP headers as a continuous string with each header on a 
				new line.
		'''
		protocol_string = 'HTTP/1.1 %i %s' % (self.status_code, STATUS_MSG_MAP[self.status_code])
		server_string = 'Server: %s' % self.server
		date_string = 'Date: %s' % self.date
		etag_string = 'ETag: %s' % self.hash
		content_type_string = 'Content-Type: %s' % self.content_type
		content_length_string = 'Content-Length: %i' % self.content_length

		main_str = ''
		main_str += protocol_string + '\r\n'
		main_str += server_string + '\r\n'
		main_str += date_string + '\r\n'
		main_str += etag_string + '\r\n'
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
