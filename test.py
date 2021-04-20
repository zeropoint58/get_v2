import re
import time

import requests
from pyquery import PyQuery

if __name__ == '__main__':
    new_v2ray_url = 'https://www.mattkaydiary.com/2021/04/2021-04-19-free-v2ray-clash-vmess-trojan.html'

    proxies = {"http": "http://localhost:1081", "https": "http://localhost:1081", }
    new_v2ray_data = requests.get(new_v2ray_url, proxies=proxies)
    new_v2ray_data_html = new_v2ray_data.text
    doc = PyQuery(new_v2ray_data_html)
    s = re.findall('https?://drive.google.com/uc\Sexport=download&id=\S+', doc.text())
    for i, val in enumerate(s):
        if i % 2 == 0:
            v2File = requests.get(val, proxies=proxies)
            v2FileName = 'vv{}'.format(i)
            with open(v2FileName, 'wb') as f:
                f.write(v2File.content)