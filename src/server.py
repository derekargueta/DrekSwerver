__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'


from datetime import datetime
from debug import debug_print
import errno
import select
import settings
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
		self.caches = {}  # cache per client
		self.socket_timing = {}  # to keep track of timing out
		timeout_check = (None, None)
		self.size = 1024

	def open_socket(self) -> None:
		"""
			Set up a socket on which to accept incoming client requests
		"""
		try:
			debug_print('Opening socket')
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((self.host, self.port))
			self.server.listen(5)
			self.server.setblocking(False)
		except socket.error as err:
			if self.server:
				self.server.close()
			print('Could not open socket: %s' % err)
			sys.exit(1)

	def _check_timeout(self) -> None:
		"""
			This function will loop over sockets and check if any sockets
			are overdue to be timed out. Timed out sockets are killed using
			_shutdown_socket
		"""
		bad = []  # we can't mod the dictionary while iterating, so keep track of
				  # sockets to kill in this `bad` list
		for k, v in self.socket_timing.items():
			current_time = datetime.now()
			if int((current_time-v).total_seconds()) > int(settings.TIMEOUT):
				# socket timeout, kill it
				bad.append(k)

		# kill any sockets that should timeout
		for socket in bad:
			self._shutdown_socket(socket)

	def run(self) -> None:
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
				if file_descriptor in self.socket_timing:
					self.socket_timing[file_descriptor] = datetime.now()
				if event & (select.POLLHUP | select.POLLERR):
					self.handle_error(file_descriptor)
					continue
				if file_descriptor == self.server.fileno():
					self.handle_server()
					continue
				result = self.handle_client(file_descriptor)
			self._check_timeout()

	def handle_error(self, file_descriptor) -> None:
		''' Handler if the poller detects an error. Will try to repoen the socket
				but if that fails then the program just exits.
		'''

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

	def handle_server(self) -> None:
		# accept as many clients as possible
		while True:
			try:
				client, address = self.server.accept()
			except socket.error as err:
				# if socket blocks b/c no clients are available, then return
				if err == errno.EAGAIN or errno.EWOULDBLOCK:
					return
				print(traceback.format_exc())
				sys.exit()

			# set client to be non-blocking
			client.setblocking(False)
			self.clients[client.fileno()] = client
			self.socket_timing[client.fileno()] = datetime.now()
			self.poller.register(client.fileno(), self.pollmask)

	def handle_client(self, file_descriptor) -> None:
		debug_print('Handling client with fd {0}'.format(file_descriptor))
		try:
			data = self.clients[file_descriptor].recv(self.size)
		except socket.error as err:
			# if no data is available, on to the next client
			if err == errno.EAGAIN or errno.EWOULDBLOCK:
				return
			print(traceback.format_exc())
			sys.exit()

		if data:

			split_data = data.decode('utf-8').split('\r\n\r\n')
			data_is_complete = len(split_data) > 0 and split_data[-1] == ''
			
			for piece in split_data[:-1]:
				piece += '\r\n\r\n'
				piece = self._use_cache(file_descriptor, piece)
				
				rp = RequestParser(piece)
				resp = rp.get_appropriate_response()

				# send all the HTTP headers
				self.clients[file_descriptor].send(str(resp).encode('utf-8'))

				# send the file that was requested
				if resp.status_code != 304 and resp.method == 'GET':
					self._handle_GET(file_descriptor, resp)

			# not a complete HTTP request
			if split_data[-1] != '':
				if file_descriptor in self.caches:
					self.caches[file_descriptor] += split_data[-1]
				else:
					self.caches[file_descriptor] = split_data[-1]
				split_data = split_data[0:-1]

	def _handle_GET(self, fd: int, httpresponse) -> None:
		''' Handle GET requests for the builtin file system server '''
		resp_content = httpresponse.content
		if type(resp_content) is str:
			resp_content = resp_content.encode('utf-8')
		self.clients[fd].send(resp_content)

	def _use_cache(self, fd, data) -> str:
		''' Check if there's any cached data we can use for this client.
				If there isn't, then `data` is returned unchanged.

				SIDE EFFECT: If cached data is found, it is deleted from the global
				cache after being used.
		'''
		if fd in self.caches:
			data = self.caches[fd] + data
			del self.caches[fd]
		return data


	def _shutdown_socket(self, file_descriptor) -> None:
		del self.socket_timing[file_descriptor]
		self.poller.unregister(file_descriptor)
		if file_descriptor in self.clients:
			self.clients[file_descriptor].close()
			del self.clients[file_descriptor]
		else:
			debug_print('tried to close a socket that was not in clients: %i' % file_descriptor)
