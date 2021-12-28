import os
import time
import shutil
from yamlUtils import YamlUtils

changfengoss = os.path.join("changfengoss")
dirname = time.strftime("%Y_%m_%d", time.localtime(time.time()))

yamlUtils = YamlUtils(changfengoss)
yamlUtils.clone_repo("https://github.com/changfengoss/pub.git")
yamlUtils.make_template_dict(dirname)
yamlUtils.save_file("changfengoss.yaml")
shutil.rmtree(changfengoss)

bhqz = os.path.join("bhqz")
yamlUtils = YamlUtils(bhqz)
yamlUtils.clone_repo("https://github.com/bhqz/bhqz.git")
yamlUtils.make_template_dict()
yamlUtils.save_file("bhqz.yaml")
shutil.rmtree(bhqz)
