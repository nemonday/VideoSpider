from pprint import pprint

import requests
import re

url = 'http://toutiao.com/group/6697877526292726279/'

# https://www.ixigua.com/i6697877526292726279/

rep = re.search(r'http://toutiao.com/group/(.*)/', url).group(1)
url = 'https://www.ixigua.com/i' + rep + '/'

print(url)



