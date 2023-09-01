
from os import listdir
from os.path import getmtime, isfile, isdir

from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout

# from pygame.time import Clock
from time import sleep

from local.utils import join, thread, File, Dir
from local.http import User, Request, Response


class Server:
	socket = None
	running = True

	def __init__(self, path, port=80, host=''):
		self.addr = (host, port)
		self.cache = Dir(path)

	# *безопасное закрытие сервера
	def close(self):
		if self.socket is None: return
		try: self.socket.close()
		except: raise # какие тут исключения могут вылезти?
		self.socket = None

	# функция остановки для вызова из вне
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

		if parallel: thread(self.main)
		else: self.main()

	def main(self):
		while self.running:
			user = User(self.socket)
			thread(self.processing, user)

	def dir_processing(self, req, dir):
		data = b''
		if '.html' in dir:
			data = dir['.html'].read()
		if '.py' in dir:
			file = dir['.py']
			data = file(req=req, data=data)
		return data

	def response_404(self, req):
		if '404' in self.cache:
			data = self.dir_processing(req, self.cache['404'])
		else:
			req.code = 404
			data = b''
		Response(req, data)

	def processing(self, user):
		try: req = Request(user)
		except ConnectionResetError:
			user.close(); return

		if req.code == 400:
			print('Ошибка:', user.addr)
			print(req.raw_data, '\n')
			Response(req)
			return

		print(user.addr)
		print(req.raw_data, '\n')

		self.cache.check()
		if (req.path in self.cache) or (not req.path):
			if req.path:
				obj = self.cache[req.path]
			else:
				obj = self.cache

			if obj.type == 0: # обработка директории
				data = self.dir_processing(req, obj)
				if data:
					Response(req, data)
				else:
					self.response_404(req)
		
			elif obj.type == 1: # обработка файла
				if req.path.endswith('.html'): type = 'html'
				elif req.path.endswith('.css'): type = 'css'
				elif req.path.endswith('.js'): type = 'js'
				else: type = '*'
				Response(req, obj.read() or b'', type=type)

		else:
			self.response_404(req)

if __name__ == '__main__':
	server = Server('pages')
	print(server.cache.keys(), '\n')
	server.start()