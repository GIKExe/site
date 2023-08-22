
from re import findall
from requests.utils import unquote
from os.path import getmtime, isfile, isdir
from .utils import join, File


def response(data=b'', code=200, **kwagrs):
	headers = f'HTTP/1.1 {code}\r\n'
	for key, value in list(kwagrs.items()):
		if key == 'Content-Type':
			value += ';charset=UTF-8'
		headers += f'{key}: {value}\r\n'
	headers = headers.encode('UTF-8')

	if type(data) is str:
		data = data.encode('UTF-8')

	return headers + b'\r\n' + data


class Page:
	main = None

	def __init__(self, path):
		self.html = File(join(path, 'index.html'))
		if isfile(join(path, 'main.py')):
			self.main = File(join(path, 'main.py'))

	def processing(self, user, request):
		if self.main is None:
			return self.html.read()
		return self.main(user=user, request=request, data=self.html.read())


class User:
	def __init__(self, socket):
		self.socket, self.addr = socket.accept()
		self.recv = self.socket.recv
		self.send = self.socket.send
		self.close = self.socket.close


class Request:
	def __init__(self, raw_data):
		self.raw_data = raw_data
		self.code = 200
		res = (findall(r'^(.*?) /(.*?) HTTP/(.)\.(.)\r((?:\n.*?: .*?\r){1,})\n\r\n', raw_data) or [None])[0]
		if not res: self.code = 400; return
		self.command = res[0]
		self.path = unquote(res[1])
		self.version = res[2:4]
		self.headers = {key:value for key,value in findall(r'\n(.*?): (.*?)\r', res[-1])}
		self.data = raw_data.split('\r\n\r\n', 1)[-1]