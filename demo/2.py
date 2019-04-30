import os

import requests


def download_u3m8(url):
    download_path = os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
        all_content = requests.get(url).text
        file_line = all_content.split('\r\n')

        if file_line[0] != "#EXTM3U":
            raise BaseException(u'非M3U8的链接')
        else:
            unkown = True
            for index, line in enumerate(file_line):
                if "EXTINF" in line:
                    unkown=False
                    pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]
                    res = requests.get(pd_url)
                    c_fule_name = str(file_line[index + 1])
                    with open(download_path + "\\" + c_fule_name, 'ab') as f:
                        f.write(res.content)
                        f.flush()
            if unkown:
                raise BaseException("未找到对应的下载链接")
            else:
                print('下载完成')

download_u3m8('https://rescdn.yishihui.com/longvideo/sample/transcode/video/live/201904096380619J6ANO6FqcEDAxnlwRZ.m3u8')
