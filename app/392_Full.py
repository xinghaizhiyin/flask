#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import json
url = 'https://login5.spotify.com/v3/login'
headers = {'Host': 'login5.spotify.com', 'Connection': 'keep-alive', 'Content-Length': '338', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache, no-store, max-age=0', 'Content-Type': 'application/x-protobuf', 'User-Agent': 'Spotify/121000760 Win32/0 (PC desktop)', 'client-token': 'AADgazMardrfzZ6WHVQFX0ynlaKsorIXXMaIp9N7MGuQyCWf0zX9m7YkU/7rupfBX15AOwPCJ2diFc9K52mOR+JMQF7F9kljPBZzcnSsca5rAVt7ZZgj58KtsdKkBOGFA9JnTBoND/+zot93Uw/cZ0l5Y46+kWAsCCkPgDo7IL0dawKvby3yGk2U5vwlgpMlOTF2T25db2ZZCdExNDaE0AXA1ErgK2G/T6NwybJFp2iPPARr6PBhndyz3MmcGtDjYg==', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Origin': 'https://login5.spotify.com', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'no-cors', 'Sec-Fetch-Dest': 'empty', 'Accept-Encoding': 'gzip, deflate, br'}
cookies = {}
data = {}

html = requests.post(url, headers=headers,  cookies=cookies, data=json.dumps(data))
print(html)
print(html.status_code)
