# dir: user, request, data, exit (return)

from re import findall
headers = request.headers


text = ''
if 'sec-ch-ua' in headers:
	res = findall(r'"(.*?)";v="(.*?)"', headers['sec-ch-ua'])
	if res:
		name, version = res[-1]
		if name == 'YaBrowser':
			name = 'Яндекс'
		text += f'Браузер: {name} v{version}\n'

if 'sec-ch-ua-mobile' in headers:
	text += f'Устройство: {"стационарное" if headers["sec-ch-ua-mobile"] == "?0" else "мобильное"}\n'

if not text:
	text = 'В вашем запросе нет данных, которые мы можем обработать'

data = data.replace('<!-- SLDJFLIJWLI -->'.encode('UTF-8'),
	text.replace('\n','<br>').replace('\t', '').encode('UTF-8'), 1)

data = data.replace('<!-- SLDJFLIJWLI -->'.encode('UTF-8'),
	request.raw_data.replace('\n','<br>').replace('\r', '').encode('UTF-8'), 1)

exit(data)