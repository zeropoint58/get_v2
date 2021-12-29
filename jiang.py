import json
import requests


if __name__ == "__main__":
    # proxies = {
    #     "http": "http://localhost:1080",
    #     "https": "http://localhost:1080",
    # }
    # proxies = {}

    url = "https://api.dler.io/sub?target=clash&new_name=true&url=https://jiang.netlify.app&insert=false&config=https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online.ini"
    file = requests.get(url, proxies=proxies)
    headers = json.dumps(dict(file.headers))
    with open("jiang.yaml", "wb") as f:
        f.write(file.content)
