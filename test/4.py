import json
import time

import requests

proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
proxy = requests.get(proxy_url)
print(proxy.text)
proxy = json.loads(proxy.text)['data'][0]
proxies = {
    'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
}

print(proxies['https'])
isotimeformat = '%Y-%m-%d'
a = time.strftime(isotimeformat, time.localtime(time.time()))

print(a)