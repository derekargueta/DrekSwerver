__author__ = 'Derek Argueta'
__email__ = 'darguetap@gmail.com'

SUPPORTED_METHODS = ['GET', 'HEAD']

STATUS_MSG_MAP = {
	200: 'GET',
	206: 'Partial Content',
  304: 'Not Modified',
	400: 'Bad Request',
	403: 'Forbidden',
	404: 'Not Found',
	500: 'Internal Server Error',
	501: 'Not Implemented'
}