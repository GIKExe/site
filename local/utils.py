
from os.path import getmtime, isfile, isdir
from threading import Thread


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

	def __init__(self, path):
		self.path = path
		self.check()

	def __call__(self, *args, **kwargs):
		self.check()
		text = self.data.decode('UTF-8')
		return dexec(text, **kwargs)

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