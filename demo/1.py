import requests

url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=100017&port=1&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='

data = requests.get(url)

print(data.text)

