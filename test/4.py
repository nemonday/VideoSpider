import json

import requests

from VideoSpider.API.iduoliao import Iduoliao

item = {}
url = 'https://api.xiaoniangao.cn/trends/get_recommend_trends'

xng_zf_headers = {
    'charset': 'utf-8',
    'Accept-Encoding': 'gzip',
    'referer': 'https://servicewechat.com/wx018f668a2cd22af8/18/page-frame.html',
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MIX Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Safari/537.36 MicroMessenger/7.0.3.1400(0x2700033B) Process/appbrand0 NetType/WIFI Language/zh_CN',
    'Host': 'api.xiaoniangao.cn',
    'Connection': 'Keep-Alive',
}

data = r"""{"uid":"2b213f38-f682-4c3b-8e2d-089c84190684","proj":"ma-topic-blessing","wx_ver":"7.0.1","code_ver":"1.1.0","tag_id":108,"log_params":{"page":"topic","common":{"os":"iOS 12.2","device":"iPhone 6s","weixinver":"7.0.1","srcver":"2.5.2"}},"qs":"imageMogr2/gravity/center/rotate/$/thumbnail/!750x500r/crop/750x500/interlace/1/format/jpg","h_qs":"imageMogr2/gravity/center/rotate/$/thumbnail/!80x80r/crop/80x80/interlace/1/format/jpg","share_width":625,"share_height":500,"token":"12075f07b016d34a27db743df4589c12"}"""

res = requests.post(url, headers=xng_zf_headers, data=data, timeout=30)
json_data = json.loads(res.text)

video_datas = json_data['data']['list']
for video in video_datas:
    item['url'] = video['v_url']
    item['download_url'] = video['v_url']
    item['like_cnt'] = video['favor']['total']
    item['cmt_cnt'] = 0
    item['sha_cnt'] = 0
    item['view_cnt'] = video['views']
    item['thumbnails'] = video['url']
    item['title'] = video['title']
    item['id'] = video['album_id']
    item['video_height'] = video['vw']
    item['video_width'] = video['w']
    item['from'] = '小年糕祝福'
    item['old_type'] = '父亲节'
    # 筛选条件
    if item['view_cnt'] >= item['view_cnt_compare']:
        # 开始去水印上传
        Iduoliao.upload(item['url'], item['thumbnails'], item['osskey'], '小年糕祝福', item['title'], item['old_type'])
