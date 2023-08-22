
from os import listdir
from os.path import getmtime, isfile, isdir

from socket import socket as Socket, AF_INET, SOCK_STREAM, timeout

from local.utils import join, thread
from local.http import response, Page, User, Request


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
