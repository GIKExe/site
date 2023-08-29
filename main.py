
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
		self.cache[''] = self.cache

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

	def get_data_from_page(self, req):
		if req.path in self.cache:
			obj = self.cache[req.path]

			if '.html' in obj:
				data = obj['.html'].read()
			else:
				data = b''

			if '.py' in obj:
				file = obj['.py']
				data = file(req=req, data=data)
			return data

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
		if req.path in self.cache:
			obj = self.cache[req.path]
			if obj.type:
				if req.path.endswith('.css'): type = 'css'
				elif req.path.endswith('.js'): type = 'js'
				else: type = '*'
				Response(req, obj.read() or b'', type=type)
			else:
				data = self.get_data_from_page(req)
				Response(req, data)
		else:
			if '404' in self.cache:
				req.path = '404'
				data = self.get_data_from_page(req)
			else:
				req.code = 404
				data = b''
			Response(req, data)


if __name__ == '__main__':
	server = Server('pages')
	print(server.cache.keys(), '\n')
	server.start()