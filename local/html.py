

class page:
	def Error(code='—', msg='—'):
		return f'''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>{code}</title>
</head>
<body style="font-family: Arial;">
	<h1>Код ошибки: {code}</h1>
	<h2>Сообщение: {msg}</h2>
</body>
</html>'''.encode('UTF-8')