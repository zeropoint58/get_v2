import os
import re
import time
from shutil import copyfile

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

if __name__ == '__main__':
    url = "https://www.mattkaydiary.com/"

    data = requests.get(url)
    text = data.text
    soup = BeautifulSoup(text, 'lxml')
    div_list = soup.select('h2.post-title > a')
    new_v2ray_url = div_list[0].get('href')
    new_v2ray_data = requests.get(new_v2ray_url)
    new_v2ray_data_html = new_v2ray_data.text
    doc = PyQuery(new_v2ray_data_html)
    s = re.findall('https?://drive.google.com/uc\Sexport=download&id=\S+', doc.text())
    v2File = requests.get(s[0])
    v2FileName = 'vv'
    with open(v2FileName, 'wb') as f:
        f.write(v2File.content)
