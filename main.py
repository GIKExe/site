
import os
from os import listdir
from os.path import getmtime, isfile, isdir, join

from re import findall
from datetime import datetime
from requests.utils import unquote
from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread


def join(*args):
	if args[0] == '':
		args = args[1:]
	return '/'.join(args)


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


class ExecInterrupt(Exception): pass
class File:
	time = -1

	def __init__(self, path):
		self.path = path
		self.check()

	def __call__(self, *args, **kwargs):
		self.check()
		text = self.data.decode('UTF-8')
		RETURN = []
		def _exit(*args, **kwargs):
			RETURN.append(args)
			raise ExecInterrupt
		
		kwargs['exit'] = _exit
		try: exec(text, kwargs)
		except ExecInterrupt: pass

		if len(RETURN) > 0:
			if len(RETURN[0]) == 1:
				return RETURN[0][0]
			return RETURN[0]

	def check(self):
		if not isfile(self.path):
			raise Exception(f'"{self.path}" не является файлом.')

		new_time = getmtime(self.path)
		if self.time != new_time:
			with open(self.path, 'rb') as file:
				self.data = file.read()
			self.time = new_time

	def read(self):
		self.check()
		return self.data

	def write(self):
		with open(self.path, 'wb') as file:
			file.write(self.data)


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


class Server:
	socket = None
	running = True

	def __init__(self, port=80, host=''):
		self.addr = (host, port)
		self.cache = {}

	def connect_dir(self, path, site_path=''):
		# надо бы добавить отслеживание изменений в директории...
		if not isdir(path): return
		if isfile(join(path, 'index.html')):
			self.cache[site_path] = Page(path)

		for name in listdir(path):
			if isdir(join(path, name)):
				self.connect_dir(join(path, name), join(site_path, name))

	def close(self):
		if self.socket is None: return
		try: self.socket.close()
		except: raise # какие тут исключения могут вылезти?
		self.socket = None

	def stop(self):
		self.running = False
		self.close()

	def create_socket(self):
		self.close()
		self.socket = Socket(AF_INET, SOCK_STREAM)
		try:
			self.socket.bind(self.addr)
		except:
			self.socket = None
			raise
		else:
			self.socket.listen()

	def start(self, parallel=False):
		self.create_socket()

		if parallel:
			Thread(target=self.main, daemon=True).start()
		else:
			self.main()

	def main(self):
		while self.running:
			user = User(self.socket)
			Thread(target=self.processing, args=(user,), daemon=True).start()

	def get_page(self, key):
		if key not in self.cache:
			if '404' not in self.cache:
				return 404, None
			key = '404'
		page = self.cache[key]
		return 200, page

	def processing(self, user):
		raw_data = user.recv(1024).decode('UTF-8')
		request = Request(raw_data)

		data = b''
		if request.code != 400:
			request.code, page = self.get_page(request.path)
			if request.code != 404:
				data = page.processing(user, request)

		res_data = response(data, code=request.code, **{
			'Connection': 'close',
			'Content-Type': 'text/html'
		})
		user.send(res_data)
		user.close()


if __name__ == '__main__':
	server = Server()
	server.connect_dir('pages')
	print(server.cache.keys())
	server.start()


'''
GET / HTTP/1.1\r\n
Host: localhost\r\n
Connection: keep-alive\r\n
Cache-Control: max-age=0\r\n
sec-ch-ua: "Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"\r\n
sec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\n
Upgrade-Insecure-Requests: 1\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.2.767 Yowser/2.5 Safari/537.36\r\n
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\n
Sec-Fetch-Site: none\r\n
Sec-Fetch-Mode: navigate\r\n
Sec-Fetch-User: ?1\r\n
Sec-Fetch-Dest: document\r\n
Accept-Encoding: gzip, deflate, br\r\n
Accept-Language: ru,en;q=0.9,uk;q=0.8\r\n\r\n
'''