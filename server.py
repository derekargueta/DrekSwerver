__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'


from debug import debug_print
import errno
import select
import socket
import sys
import traceback

from request import RequestParser
from response import HttpResponse, HttpResponseNotImplemented
from http_consts import SUPPORTED_METHODS


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
		try:
			data = self.clients[file_descriptor].recv(self.size)
		except socket.error, (value, msg):
			# if no data is available, on to the next client
			if value == errno.EAGAIN or errno.EWOULDBLOCK:
				return
			print(traceback.format_exc())
			sys.exit()

		debug_print('sent data:')
		debug_print(data)

		if data:

			rp = RequestParser(data)
			resp = rp.get_appropriate_response()
			self.clients[file_descriptor].send(str(resp))
			self.clients[file_descriptor].send(resp.content)
		else:
			self.poller.unregister(file_descriptor)
			self.clients[file_descriptor].close()
			del self.clients[file_descriptor]
