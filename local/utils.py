
from os import listdir
from os.path import getmtime, isfile, isdir, exists
from threading import Thread
from time import time, sleep

def join(*args):
	if args[0] == '':
		args = args[1:]
	return '/'.join(args)


def thread(fucn, *args, **kwargs):
	th = Thread(target=fucn, args=args, kwargs=kwargs, daemon=True)
	th.start()
	return th


# функция, выполняющая код в строке как функцию.
class ExecExit(Exception): pass
def dexec(text, **kwargs):
	RETURN = []
	def _exit(*args):
		RETURN.append(args)
		raise ExecExit
	kwargs['exit'] = _exit
	try: exec(text, kwargs)
	except ExecExit: pass
	if len(RETURN[0]) == 1:
		return RETURN[0][0]
	if len(RETURN) > 1:
		return RETURN[0]


class File:
	time = -1
	check_time = -1
	data = b''
	deleted = False

	def __init__(self, path=None):
		self.path = path
		self.check(log=False)

	def __call__(self, *args, **kwargs):
		# self.check()
		text = self.data.decode('UTF-8', errors='IGNORE')
		return dexec(text, **kwargs)

	def check(self, log=True):
		if self.deleted:
			return
		if time() - self.check_time < 1:
			return
		if not isfile(self.path):
			self.data = b''
			self.deleted = True
			return

		new_time = getmtime(self.path)
		if self.time != new_time:
			with open(self.path, 'rb') as file:
				self.data = file.read()
			self.time = new_time
			if log: print('файл обновлён:', self.path)
		self.check_time = time()

	def read(self):
		# self.check()
		return self.data

	def write(self):
		with open(self.path, 'wb') as file:
			file.write(self.data)


class Dir(dict):
	time = -1
	check_time = -1
	deleted = False

	def __init__(self, path):
		self.path = path
		self.check(log=False)

	def __missing__(self, key):
		if '/' not in key: raise Exception('ошибка, такого ключа не нет')
		key, path = key.split('/', 1)
		if key not in self: raise Exception('ошибка, такого ключа не нет')
		return self[key][path]

	def __contains__(self, key):
		if '/' not in key: return key in self.keys()
		key, path = key.split('/', 1)
		if key not in self: return False
		return path in self[key]
			
	def check(self, log=True):
		if self.deleted:
			return
		if time() - self.check_time < 5:
			return
		if not isdir(self.path):
			self.deleted = True; return

		for name, obj in list(self.items()):
			if obj == self: continue
			obj.check()
			if obj.deleted:
				del self[name]
				print('объект удалён:', obj.path)

		new_time = getmtime(self.path)
		if self.time != new_time:
			for name in listdir(self.path):
				if name in self.keys(): continue
				path = join(self.path, name)
				if isdir(path):
					self[name] = Dir(path)
					if log: print('добавлена директория:', path)
				elif isfile(path):
					self[name] = File(path)
					if log: print('добавлен файл:', path)

			self.time = new_time
		self.check_time = time()


if __name__ == '__main__':
	d = Dir('../pages')
	f = File('../pages/.html')

	print(type(f) is File, type(f) == File)
	print(type(f) is Dir, type(f) == Dir)