import re
import requests
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Bearer miku',
    # 'Authsign': 'd955e319b681a457f2eabd2425b334b8a974272fb25f1ccfa899a9a043a76203.U2FsdGVkX19Kk/Vct12sXmmDUcaDS44ccny+Zew9gzc=',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://miku.tools',
    'Referer': 'https://miku.tools/tools/pipixia_video_downloader',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
}

data = r'{"url":"https://h5.pipix.com/item/6629479061435455748"}'

url = 'https://api.imiku.me/node/pipixia_video_downloader'
req = requests.post(url, headers=headers, data=data)
print(req.text)