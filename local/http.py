
from re import findall
from requests.utils import unquote
from os.path import getmtime, isfile, isdir
from .utils import join, File


# class Page:
# 	main = None

# 	def __init__(self, path):
# 		self.html = File(join(path, 'index.html'))
# 		if isfile(join(path, 'index.py')):
# 			self.main = File(join(path, 'index.py'))

# 	def processing(self, req):
# 		if self.main is None:
# 			return self.html.read()
# 		return self.main(req=req, data=self.html.read())


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
		if version != 'HTTP/1.1': print('5 ', end=''); return
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


# def response(data=b'', code=200, **kwagrs):
# 	headers = f'HTTP/1.1 {code}\r\n'
# 	if 'Connection' not in kwagrs:
# 		kwagrs['Connection'] = 'close'
# 	for key, value in list(kwagrs.items()):
# 		headers += f'{key}: {value}\r\n'
# 	headers = headers.encode('UTF-8')

# 	if type(data) is str:
# 		data = data.encode('UTF-8')

# 	return headers + b'\r\n' + data


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