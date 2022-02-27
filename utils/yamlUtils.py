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
        self.not_support_ciphers = ["chacha20", "rc4", "none"]
        self.not_support_alterIds = ["undefined"]
        self.not_support_type = ["vless"]
        self.network = ["grpc", "h2"]

        self.proxies_md5_dict = dict()
        self.filtered_rules = list()
        self.proxy_names_set = set()
        with open("template.json", "r", encoding="utf8") as template_file:
            self.template = json.load(template_file)
        with open("adguard_dns.json", "r", encoding="utf8") as template_file:
            self.adguard_dns = json.load(template_file)

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
        self.make_template(log_list, keyword, dirname)

    def make_template(self, filelist, keyword="yaml", dirname=None):
        def check_proxy(proxy):
            return (
                "server" in proxy
                and proxy.get("cipher") not in self.not_support_ciphers
                and proxy.get("alterId") not in self.not_support_alterIds
                and proxy.get("type") not in self.not_support_type
                and type(proxy.get("port") == int)
                and proxy.get("port") > 0
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
                                    proxy["port"] = int(proxy.get("port"))
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
                                                + item
                                                + "_"
                                                + str(round(time.time() * 1000))
                                                + uuid.uuid4()
                                            )
                                        self.proxy_names_set.add(proxy.get("name"))
                                        self.proxies_md5_dict[data_md5] = proxy
                except Exception as e:
                    print(item)
                    print(e)

        for item in self.template["proxy-groups"]:
            proxies = item.get("proxies")
            if "DIRECT" not in proxies and "REJECT" not in proxies:
                proxies.extend(self.proxy_names_set)
            item["proxies"] = proxies

        def get_final_rule(items, group):
            if "节点选择" in group or "自动选择" in group:
                items.append("🔰 节点选择")
                return True
            elif "国外媒体" in group:
                items.append("🌍 国外媒体")
                return True
            elif "国内媒体" in group or "微软服务" in group:
                items.append("🌏 国内媒体")
                return True
            elif "电报信息" in group:
                items.append("📲 电报信息")
                return True
            elif "苹果服务" in group:
                items.append("🍎 苹果服务")
                return True
            elif "全球直连" in group:
                items.append("🎯 全球直连")
                return True
            elif "AdBlock" in group or "应用净化" in group or "全球拦截" in group:
                items.append("🛑 全球拦截")
                return True
            elif "漏网之鱼" in group or "谷歌FCM" in group:
                items.append("🐟 漏网之鱼")
                return True
            else:
                items.append(group)
                return False

        filtered_rules_set = set()
        for item in self.filtered_rules:
            if "USER-AGENT" not in item and "FINAL" not in item:
                items = item.replace(",no-resolve", "").split(",")
                group = items.pop(len(items) - 1)
                if len(items) == 2 or len(items) == 1:
                    get_final_rule(items, group)
                    filtered_rules_set.add(",".join(items))
                elif len(items) == 3:
                    new_items = list()
                    for i in range(0, len(items)):
                        get_final_rule(new_items, items[i])
                    if get_final_rule(new_items, group):
                        filtered_rules_set.add(",".join(new_items))

        self.template["proxies"] = list(self.proxies_md5_dict.values())
        self.template["rules"] = list(filtered_rules_set)

    def get_template_dict(self):
        return self.template

    def save_file(self, savepath=None, with_adguard_dns=False):
        if savepath is not None:
            template = copy.deepcopy(self.template)
            if with_adguard_dns:
                template["dns"] = self.adguard_dns
            yml = yaml.YAML()
            yml.indent(mapping=2, sequence=4, offset=2)
            with open(savepath, "w+", encoding="utf8") as outfile:
                yml.dump(template, outfile)

    def save_file_without_providers(self, savepath=None, with_adguard_dns=False):
        if savepath is not None:
            template = copy.deepcopy(self.template)
            template.pop("rule-providers")
            if with_adguard_dns:
                template["dns"] = self.adguard_dns
            yml = yaml.YAML()
            yml.indent(mapping=2, sequence=4, offset=2)
            with open(savepath, "w+", encoding="utf8") as outfile:
                yml.dump(template, outfile)
