# import requests
#
# headers = {
#      "@type": "type.googleapis.com/ja.common.proto.ReqHead",
#      "ver": '1',
#      "platform": '2',
#      "mbits": "3",
#      "lbits": "4",
# 	 "offset": '0',
# 	 "count": '10000',
#      "authorLabelType": '11'
#     "offset":'0',
# 	"count":'10000'
#     "authorLabelType":11
#
# }
#
#
# url = 'http://10.168.0.115:8080/works/SWorksAuthor/GetAuthorsAuthInfoNew'
#
# data = requests.get(url, headers=headers)
#
# print(data.text)