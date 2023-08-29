# dir: req, data, exit (return)

from re import findall, sub
from requests import get

headers = req.headers.copy()
if 'Referer' in headers:
	del headers['Referer']
if 'Cookie' in headers:
	del headers['Cookie']

try:
	text = get(req.path_data, headers=headers).text
except:
	# request.code = 404
	exit(data.replace(b'<!-- SLDJFLIJWLI -->', req.path_data.encode('UTF-8')))

# прямая ссылка на стиль
text = sub('href="/etc/styles3.css"', 'href="https://ilibrary.ru/etc/styles3.css"', text)

# удобный текст для чтения
text = sub(r'<[bB][oO][dD][yY]>', '<body style="font-family: Arial">', text)

# перезапись ссылок страниц
text = sub(r'href="/text/', 'href="/book?https://ilibrary.ru/text/', text)

data = text.encode('UTF-8')
exit(data)