import re
import time

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

if __name__ == '__main__':
    url = "https://www.mattkaydiary.com/"

    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": "localhost",
        "port": "1081",
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta
    }

    data = requests.get(url, proxies=proxies)
    text = data.text
    soup = BeautifulSoup(text, 'lxml')
    div_list = soup.select('h2.post-title > a')
    new_v2ray_url = div_list[0].get('href')
    new_v2ray_data = requests.get(new_v2ray_url, proxies=proxies)
    new_v2ray_data_html = new_v2ray_data.text
    doc = PyQuery(new_v2ray_data_html)
    s = re.findall('https?://drive.google.com/uc\Sexport=download&id=\S+', doc.text())
    v2File = requests.get(s[0], proxies=proxies)
    v2FileName = time.strftime('%Y%m%d', time.localtime(time.time())) + '_v2ray'
    with open(v2FileName, 'wb') as f:
        f.write(v2File.content)
