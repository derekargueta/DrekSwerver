__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

from response import *
from http_consts import SUPPORTED_METHODS


BAD_REQUEST_HTML = 'pages/400.html'
FORBIDDEN_HTML = 'pages/403.html'
NOT_FOUND_HTML = 'pages/404.html'
SERVER_ERROR_HTML = 'pages/500.html'
NOT_IMPLEMENTED_HTML = 'pages/501.html'


class RequestParser(object):

	def __init__(self, content):
		self.content = content

	def get_appropriate_response(self):

		try:
			from http_parser.parser import HttpParser
		except ImportError:
			from http_parser.pyparser import HttpParser

		p = HttpParser()
		nparsed = p.execute(self.content, len(self.content))

		if not p.is_headers_complete():
			return HttpResponseBadRequest(content_f=BAD_REQUEST_HTML, f_type='text/html')

		# check method
		if p.get_method() not in SUPPORTED_METHODS:
			return HttpResponseNotImplemented(content_f=NOT_IMPLEMENTED_HTML, f_type='text/html')

		req_file = self.content.split(' ')[1]
		if req_file == '/':
			return HttpResponse()

		try:
			open(req_file)
		except IOError as (errno, strerror):
			if errno == 13:
				return HttpResponseForbidden(content_f=FORBIDDEN_HTML, f_type='text/html')
			elif errno == 2:
				return HttpResponseNotFound(content_f=NOT_FOUND_HTML, f_type='text/html')

		return HttpResponseServerError(content_f=SERVER_ERROR_HTML, f_type='text/html')
