import json
from pprint import pprint

from aliyunsdkcore import client
from aliyunsdkmts.request.v20140618 import AddWaterMarkTemplateRequest
from aliyunsdkcore import client
from aliyunsdkmts.request.v20140618 import SearchTemplateRequest
from getwater import wather

clt = client.AcsClient('LTAI2aU1LjHOWKZf','fe1L3bkeucrrEFnaJbDC5woepupNAv' ,'cn-hangzhou', True, 3, None)
# request = AddWaterMarkTemplateRequest.AddWaterMarkTemplateRequest()
# request.set_accept_format('json')
# request.set_Name('water2')
# request.set_Config('{"Width":"10","Height":"30","Dx":"10","Dy":"5","ReferPos":"TopRight","Type":"Image"}')
# result = clt.do_action(request)
# print(result)
# wather(result)


# clt = client.AcsClient(access_key ,secret_key ,region_id, True, 3, None, port)
# request = SearchTemplateRequest.SearchTemplateRequest()
# request.set_accept_format('json')
# request.set_State('All')
# result = clt.do_action(request)
# pprint(json.loads(result))

from aliyunsdkcore import client
from aliyunsdkmts.request.v20140618 import SearchWaterMarkTemplateRequest
# clt = client.AcsClient(access_key ,secret_key ,region_id, True, 3, No ne, port)
request = SearchWaterMarkTemplateRequest.SearchWaterMarkTemplateRequest()
request.set_accept_format('xml')
result = clt.do_action(request)
print(result)