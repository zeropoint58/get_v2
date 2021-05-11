import re

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

if __name__ == '__main__':
    url = "https://www.mattkaydiary.com/"
    # proxies = {"http": "http://localhost:1080", "https": "http://localhost:1080", }
    proxies = {}

    data = requests.get(url, proxies=proxies)
    text = data.text
    soup = BeautifulSoup(text, 'lxml')
    div_list = soup.select('h2.post-title > a')
    new_v2ray_url = div_list[0].get('href')
    new_v2ray_data = requests.get(new_v2ray_url, proxies=proxies)
    new_v2ray_data_html = new_v2ray_data.text
    doc = PyQuery(new_v2ray_data_html)
    s = re.findall('https?://drive.google.com/uc\Sexport=download&id=\S+', doc.text())
    file_list = ['https://raw.fastgit.org/ssrsub/ssr/master/v2ray', 'https://raw.fastgit.org/ssrsub/ssr/master/Clash.yml']
    s.extend(file_list)
    print(s)
    for i, val in enumerate(s):
        print(val)
        file = requests.get(val, proxies=proxies)
        if i % 2 == 0:
            v2FileName = 'vv{}'.format(i)
            with open(v2FileName, 'wb') as f:
                f.write(file.content)
        else:
            cFileName = 'c{}'.format(i)
            with open(cFileName, 'wb') as f:
                f.write(file.content)
