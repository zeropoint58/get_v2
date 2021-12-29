import os
import json
import time
import copy
import hashlib
from ruamel import yaml
from git.repo import Repo
from git.repo.fun import is_git_dir


class YamlUtils:
    def __init__(self, local_path="./"):
        self.local_path = local_path
        self.template = {
            "port": 7890,
            "socks-port": 7891,
            "allow-lan": True,
            "mode": "Rule",
            "log-level": "info",
            "external-controller": "0.0.0.0:9090",
            "proxies": [],
            "proxy-groups": [],
            "rules": [],
        }

        self.proxy_groups_default = [
            {"name": "🔰 节点选择", "type": "select", "proxies": ["♻️ 自动选择", "🎯 全球直连"]},
            {
                "name": "♻️ 自动选择",
                "type": "url-test",
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300,
                "proxies": [],
            },
            {
                "name": "🌍 国外媒体",
                "type": "select",
                "proxies": ["🔰 节点选择", "♻️ 自动选择", "🎯 全球直连"],
            },
            {"name": "🌏 国内媒体", "type": "select", "proxies": ["🎯 全球直连", "🔰 节点选择"]},
            {"name": "📲 电报信息", "type": "select", "proxies": ["🔰 节点选择", "🎯 全球直连"]},
            {
                "name": "🍎 苹果服务",
                "type": "select",
                "proxies": ["🔰 节点选择", "🎯 全球直连", "♻️ 自动选择"],
            },
            {"name": "🎯 全球直连", "type": "select", "proxies": ["DIRECT"]},
            {"name": "🛑 全球拦截", "type": "select", "proxies": ["REJECT", "DIRECT"]},
            {
                "name": "🐟 漏网之鱼",
                "type": "select",
                "proxies": ["🔰 节点选择", "🎯 全球直连", "♻️ 自动选择"],
            },
        ]

        self.not_support_ciphers = ["chacha20", "rc4", "none"]
        self.not_support_alterIds = ["undefined"]
        self.not_support_type = ["vless"]
        self.network = ["grpc", "h2"]

        self.proxies_md5_dict = dict()
        self.filtered_rules = list()
        self.proxy_names_set = set()

    def clone_repo(self, repo_url, branch=None):
        git_local_path = os.path.join(self.local_path, ".git")
        if not is_git_dir(git_local_path):
            Repo.clone_from(repo_url, to_path=self.local_path, branch=branch)
        else:
            self.pull()

    def pull(self):
        repo = Repo(self.local_path)
        repo.git.pull()

    def make_template_dict(self, keyword="yaml", dirname=None):
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)
        repo = Repo(self.local_path)
        # 2 days ago
        # git log --since='date -d "yesterday" +%Y.%m.%d' --name-only --pretty=format:""
        commit_log = repo.git.log(
            "--since='date -d \"yesterday\" +%Y.%m.%d'",
            "--name-only",
            '--pretty=format:""',
        )
        log_list = commit_log.split("\n")
        self.make_template(log_list)

    def make_template(self, filelist, keyword="yaml", dirname=None):
        def check_proxy(proxy):
            return (
                proxy.get("cipher") not in self.not_support_ciphers
                and proxy.get("alterId") not in self.not_support_alterIds
                and proxy.get("type") not in self.not_support_type
                and type(proxy.get("port") == int)
            )

        for item in filelist:
            if (dirname is None or dirname in item) and keyword in item:
                try:
                    file_path = os.path.join(self.local_path, item)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        with open(file_path, "r", encoding="utf8") as yaml_file:
                            yaml_obj = yaml.safe_load(yaml_file)
                            rules = yaml_obj.get("rules")
                            proxies = yaml_obj.get("proxies")
                            self.filtered_rules.extend(rules)
                            for proxy in proxies:
                                if check_proxy(proxy):
                                    if proxy.get(
                                        "network"
                                    ) in self.network and not proxy.get("tls"):
                                        continue
                                    proxy_copy = copy.deepcopy(proxy)
                                    proxy_copy.pop("name")
                                    data_md5 = hashlib.md5(
                                        json.dumps(proxy_copy, sort_keys=True).encode(
                                            "utf-8"
                                        )
                                    ).hexdigest()
                                    if data_md5 not in self.proxies_md5_dict:
                                        if proxy.get("name") in self.proxy_names_set:
                                            proxy["name"] = (
                                                proxy.get("name")
                                                + "_"
                                                + str(round(time.time() * 1000))
                                            )
                                        self.proxy_names_set.add(proxy.get("name"))
                                        self.proxies_md5_dict[data_md5] = proxy
                except Exception as e:
                    print(item)
                    print(e)

        for item in self.proxy_groups_default:
            proxies = item.get("proxies")
            if "DIRECT" not in proxies and "REJECT" not in proxies:
                proxies.extend(self.proxy_names_set)
            item["proxies"] = proxies

        def get_final_rule(items, group):
            if "节点选择" in group or "自动选择" in group:
                items.append("🔰 节点选择")
            elif "国外媒体" in group:
                items.append("🌍 国外媒体")
            elif "国内媒体" in group or "微软服务" in group:
                items.append("🌏 国内媒体")
            elif "电报信息" in group:
                items.append("📲 电报信息")
            elif "苹果服务" in group:
                items.append("🍎 苹果服务")
            elif "全球直连" in group:
                items.append("🎯 全球直连")
            elif "AdBlock" in group or "应用净化" in group or "全球拦截" in group:
                items.append("🛑 全球拦截")
            elif "漏网之鱼" in group or "谷歌FCM" in group:
                items.append("🐟 漏网之鱼")
            else:
                items.append(group)

        filtered_rules_set = set()
        for item in self.filtered_rules:
            items = item.split(",")
            group = items.pop(len(items) - 1)
            if len(items) == 2 or len(items) == 1:
                get_final_rule(items, group)
                filtered_rules_set.add(",".join(items))
            elif len(items) == 3:
                new_items = list()
                for i in range(0, len(items)):
                    get_final_rule(new_items, items[i])
                new_items.append(group)
                filtered_rules_set.add(",".join(new_items))

        self.template["proxies"] = list(self.proxies_md5_dict.values())
        self.template["proxy-groups"] = self.proxy_groups_default
        self.template["rules"] = list(filtered_rules_set)

    def get_template_dict(self):
        return self.template

    def save_file(self, savepath=None):
        if savepath is not None:
            yml = yaml.YAML()
            yml.indent(mapping=2, sequence=4, offset=2)
            with open(savepath, "w+", encoding="utf8") as outfile:
                yml.dump(self.template, outfile)
