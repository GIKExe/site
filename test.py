
import re

class Request:
	def __init__(self, request_text):
		self.code = 200
		res = (re.findall(r'^(.*?) /(.*?) HTTP/(.)\.(.)\r((?:\n.*?: .*?\r){1,})\n\r\n', request_text) or [None])[0]
		if not res: self.code = 400; return
		self.command, self.path = res[:2]
		self.version = res[2:4]
		self.headers = {key:value for key,value in re.findall(r'\n(.*?): (.*?)\r', res[-1])}
		self.data = request_text.split('\r\n\r\n', 1)[-1]

text = '''GET /home HTTP/1.1\r
Host: localhost\r
Connection: keep-alive\r
Cache-Control: max-age=0\r
sec-ch-ua: "Not.A/Brand";v="8", "Chromium";v="114", "YaBrowser";v="23"\r
sec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r
Upgrade-Insecure-Requests: 1\r
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.2.767 Yowser/2.5 Safari/537.36\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r
Sec-Fetch-Site: none\r
Sec-Fetch-Mode: navigate\r
Sec-Fetch-User: ?1\r
Sec-Fetch-Dest: document\r
Accept-Encoding: gzip, deflate, br\r
Accept-Language: ru,en;q=0.9,uk;q=0.8\r\n\r\nhello\nworld'''

request = Request(text)
print(request.code)
print(request.command)
print(request.path)
print([request.data])