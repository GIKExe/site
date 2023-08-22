# dir: user, request, data, exit (return)

from re import findall
headers = request.headers

# text = ''
# if 'sec-ch-ua' in headers:
# 	res = findall(r'"(.*?)";v="(.*?)"', headers['sec-ch-ua'])
# 	if res:
# 		name, version = res[-1]
# 		if name == 'YaBrowser':
# 			name = 'Яндекс'
# 		text += f'Ваш браузер: {name} v{version}\n'

# if 'sec-ch-ua-mobile' in headers:
# 	text += f'Запрос сделан с мобильного устройства: {"нет" if headers["sec-ch-ua-mobile"] == "?0" else "да"}\n'

# if not text:
# 	text = 'В вашем запросе нет данных, которые мы можем обработать'

# data = data.replace('<!-- SLDJFLIJWLI -->'.encode('UTF-8'),
# 	text.replace('\n','<br>').replace('\t', '').encode('UTF-8'), 1)

# data = data.replace('<!-- SLDJFLIJWLI -->'.encode('UTF-8'),
# 	request.raw_data.replace('\n','<br>').replace('\r', '').encode('UTF-8'), 1)

exit(data)