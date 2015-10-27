__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'


import debug
import errno
import select
import socket
import sys
import traceback

from response import Response
from http_consts import SUPPORTED_METHODS


def valid_request(message):
	try:
		from http_parser.parser import HttpParser
	except ImportError:
		from http_parser.pyparser import HttpParser

	p = HttpParser()
	nparsed = p.execute(message, len(message))
	return p.get_method() in SUPPORTED_METHODS


class Server(object):

	def __init__(self, port):
		self.host = ''
		self.port = port
		self.open_socket()
		self.clients = {}
		self.size = 1024

	def open_socket(self):
		"""
			Set up a socket on which to accept incoming client requests
		"""
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((self.host, self.port))
			self.server.listen(5)
			self.server.setblocking(0)
		except socket.error, (value, message):
			if self.server:
				self.server.close()
			print('Could not open socket: %s' % message)
			sys.exit(1)

	def run(self):
		self.poller = select.epoll()
		self.pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
		self.poller.register(self.server, self.pollmask)
		while True:
			# poll sockets
			try:
				fds = self.poller.poll(timeout=1)
			except:
				return
			for file_descriptor, event in fds:
				if event & (select.POLLHUP | select.POLLERR):
					self.handle_error(file_descriptor)
					continue
				if file_descriptor == self.server.fileno():
					self.handle_server()
					continue
				result = self.handle_client(file_descriptor)

	def handle_error(self, file_descriptor):

		debug.debug_print('aaaayyy hit an error lmaaaoooo')
		self.poller.unregister(file_descriptor)
		if file_descriptor == self.server.fileno():
			# recreate the socket
			self.server.close()
			self.open_socket()
			self.poller.register(self.server, self.pollmask)
		else:
			# close socket
			self.clients[file_descriptor].close()
			del self.clients[file_descriptor]

	def handle_server(self):
		# accept as many clients as possible
		while True:
			try:
				client, address = self.server.accept()
			except socket.error, (value, message):
				# if socket blocks b/c no clients are available, then return
				if value == errno.EAGAIN or errno.EWOULDBLOCK:
					return
				print(traceback.format_exc())
				sys.exit()

			# set client to be non-blocking
			client.setblocking(0)
			self.clients[client.fileno()] = client
			self.poller.register(client.fileno(), self.pollmask)

	def handle_client(self, file_descriptor):
		"""
			TODO - handling process
			1) check request - if bad return 400
			2) validate GET type - if no return 501
			3) check file existence - if no return 404
			4) check file permissions - if no return 403
		"""
		try:
			data = self.clients[file_descriptor].recv(self.size)
		except socket.error, (value, msg):
			# if no data is available, on to the next client
			if value == errno.EAGAIN or errno.EWOULDBLOCK:
				return
			print(traceback.format_exc())
			sys.exit()

		if data:
			with open('requirements.txt') as f:
				if valid_request(data):
					self.clients[file_descriptor].send(Response().get_response_str())
					self.clients[file_descriptor].send('asdfasdf')
				else:
					with open('pages/501.html') as cont:
						content = cont.read()
						r = Response(status=501, content=content, f_type='text/html')
						self.clients[file_descriptor].send(r.get_response_str())
						self.clients[file_descriptor].send(content)
		else:
			self.poller.unregister(file_descriptor)
			self.clients[file_descriptor].close()
			del self.clients[file_descriptor]
