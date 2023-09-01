
from re import findall
from requests.utils import unquote
from os.path import getmtime, isfile, isdir
from .utils import join, File


class User:
	def __init__(self, socket):
		self.socket, self.addr = socket.accept()
		self.recv = self.socket.recv
		self.send = self.socket.send

	def close(self):
		try: self.socket.close()
		except: pass


class Request:
	code = 400
	def __init__(self, user):
		self.user = user
		raw_data = user.recv(1024).decode('UTF-8', errors='IGNORE')
		self.raw_data = raw_data
		if not raw_data: return
		if '\r\n\r\n' not in raw_data: print('1 ', end=''); return
		raw_data, self.data = raw_data.split('\r\n\r\n', 1)
		raw_data = raw_data.replace('\r\n', '\n')
		if raw_data.count('\n') < 1: print('2 ', end=''); return
		headers = raw_data.split('\n')

		line = headers.pop(0)
		if line.count(' ') != 2: print('3 ', end=''); return
		command, path, version = line.split(' ')
		if command not in ['GET']: print('4 ', end=''); return
		self.command = command
		if version not in ['HTTP/1.1', 'HTTP/1.0']: print('5 ', end=''); return
		# self.version = version
		if '?' in path:
			path, path_data = path.split('?', 1)
		else:
			path_data = ''
		self.path = path[1:]
		self.path_data = path_data

		self.headers = {}
		for header in headers:
			if ': ' not in header: continue
			key, value = header.split(': ', 1)
			self.headers[key] = value

		self.code = 200


_type = type
class Response:
	def __init__(self, req, data=b'', type='html', close=True, **kwagrs):
		if _type(data) is str:
			data = data.encode('UTF-8')

		headers = f'''HTTP/1.1 {req.code}
Connection: {"close" if close else 'keep-alive'}
Content-type: text/{type};charset=UTF-8
'''
		for key, value in kwagrs:
			headers += f'{key}: {value}\n'

		# print(headers, '\n')
		headers = headers.replace('\n', '\r\n').encode('UTF-8')
		req.user.send(headers + b'\r\n' + data)
		if close: req.user.close()