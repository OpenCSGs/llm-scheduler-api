
from kubernetes import client, config
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
kubeConf = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config.kube_config.load_kube_config(config_file=kubeConf+"/.config")
c = client.Configuration().get_default_copy()
c.verify_ssl = False
client.Configuration().set_default(c)
