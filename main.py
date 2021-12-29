import re

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

if __name__ == "__main__":
    url = "https://www.mattkaydiary.com/"
    # proxies = {"http": "http://localhost:1080", "https": "http://localhost:1080", }
    proxies = {}

    data = requests.get(url, proxies=proxies)
    text = data.text
    soup = BeautifulSoup(text, "lxml")
    # div_list = soup.select('h2.post-title > a')
    # div_list = soup.findAll(name='a',attrs={"href":re.compile(r'https?:\/\/www\.mattkaydiary\.com\S+?free-v2ray-clash-link.html')})
    div_list = soup.findAll(
        name="a",
        attrs={"href": re.compile(r"https?:\/\/www\.mattkaydiary\.com\S+?\.html")},
    )
    a_list = []
    p = re.compile(r"\d{4}年\d{2}月\d{2}日更新")
    for i, val in enumerate(div_list[:10]):
        if p.search(val.text):
            a_list.append(val.get("href"))
    new_v2ray_url = a_list[0]
    new_v2ray_data = requests.get(new_v2ray_url, proxies=proxies)
    new_v2ray_data_html = new_v2ray_data.text
    doc = PyQuery(new_v2ray_data_html)
    s = re.findall("https?://drive.google.com/uc\Sexport=download&id=\S+", doc.text())
    file_list = [
        "https://jiang.netlify.app/",
        "https://api.dler.io/sub?target=clash&new_name=true&url=https://jiang.netlify.app&insert=false&config=https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online.ini",
    ]
    s.extend(file_list)
    print(s)
    for i, val in enumerate(s):
        print(val)
        file = requests.get(val, proxies=proxies)
        if i % 2 == 0:
            v2FileName = "vv{}".format(i)
            with open(v2FileName, "wb") as f:
                f.write(file.content)
        else:
            cFileName = "c{}".format(i)
            with open(cFileName, "wb") as f:
                f.write(file.content)
