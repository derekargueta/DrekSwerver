__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

from response import *
from http_consts import SUPPORTED_METHODS
import settings


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
			# try to use the fast C parser
			from http_parser.parser import HttpParser
		except ImportError:
			# fall back to the Python parser
			from http_parser.pyparser import HttpParser

		p = HttpParser()
		nparsed = p.execute(self.content, len(self.content))

		if not p.is_headers_complete():
			return HttpResponseBadRequest(content_f=BAD_REQUEST_HTML)

		# check method
		if p.get_method() not in SUPPORTED_METHODS:
			return HttpResponseNotImplemented(content_f=NOT_IMPLEMENTED_HTML)

		base_filepath = ''
		try:
			base_filepath = settings.HOSTS[p.get_headers()['Host'].split(':')[0]]
		except KeyError:
			base_filepath = settings.HOSTS['default']

		req_file = self.content.split(' ')[1]
		if req_file == '/':
			req_file = '/index.html'

		try:
			full_path = base_filepath + req_file
			open(full_path)
			if p.get_method() == 'HEAD':
				return HttpResponse(content_f=full_path, method='HEAD')
			if 'Range' in p.get_headers():
				return HttpResponsePartialContent(content_f=full_path, h_range=p.get_headers()['Range'])	
			return HttpResponse(content_f=full_path)
		except IOError as (errno, strerror):
			if errno == 13:
				return HttpResponseForbidden(content_f=FORBIDDEN_HTML)
			elif errno == 2:
				return HttpResponseNotFound(content_f=NOT_FOUND_HTML)

		return HttpResponseServerError(content_f=SERVER_ERROR_HTML)
